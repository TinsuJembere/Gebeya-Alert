"""
Price prediction service using historical data analysis.
Uses moving averages and simple regression for price forecasting.
"""
import logging
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, func
from fastapi import HTTPException, status

from models.price import Price
from models.crop import Crop
from models.market import Market
from schemas.price import PricePrediction, BestTimeToSell

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for price predictions and recommendations."""
    
    @staticmethod
    def get_price_history(
        db: Session,
        crop_id: int,
        market_id: int,
        days: int = 90
    ) -> List[Price]:
        """
        Get price history for a crop-market combination.
        Optimized query with date range filtering.
        
        Args:
            db: Database session
            crop_id: Crop ID
            market_id: Market ID
            days: Number of days of history to retrieve
            
        Returns:
            List of price records ordered by date
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        statement = (
            select(Price)
            .where(
                Price.crop_id == crop_id,
                Price.market_id == market_id,
                Price.price_date >= start_date,
                Price.price_date <= end_date
            )
            .order_by(Price.price_date.asc())
        )
        
        return list(db.exec(statement).all())
    
    @staticmethod
    def calculate_moving_average(prices: List[float], window: int = 7) -> float:
        """
        Calculate simple moving average.
        
        Args:
            prices: List of price values
            window: Number of days for moving average
            
        Returns:
            Moving average value
        """
        if not prices:
            return 0.0
        
        if len(prices) < window:
            return sum(prices) / len(prices)
        
        return sum(prices[-window:]) / window
    
    @staticmethod
    def calculate_simple_regression(prices: List[float]) -> Dict[str, float]:
        """
        Calculate simple linear regression slope.
        
        Args:
            prices: List of price values ordered by date
            
        Returns:
            Dictionary with slope and intercept
        """
        if len(prices) < 2:
            return {"slope": 0.0, "intercept": prices[0] if prices else 0.0}
        
        n = len(prices)
        x_values = list(range(n))
        y_values = prices
        
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x_squared = sum(x * x for x in x_values)
        
        # Calculate slope and intercept
        denominator = n * sum_x_squared - sum_x * sum_x
        if denominator == 0:
            return {"slope": 0.0, "intercept": sum_y / n}
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n
        
        return {"slope": slope, "intercept": intercept}
    
    @staticmethod
    def predict_price(
        db: Session,
        crop_id: int,
        market_id: int,
        days_ahead: int = 7
    ) -> PricePrediction:
        """
        Predict price for a crop-market combination.
        
        Args:
            db: Database session
            crop_id: Crop ID
            market_id: Market ID
            days_ahead: Number of days to predict ahead
            
        Returns:
            PricePrediction object
        """
        # Validate crop and market exist
        crop = db.get(Crop, crop_id)
        market = db.get(Market, market_id)
        
        if not crop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crop with ID {crop_id} not found"
            )
        
        if not market:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Market with ID {market_id} not found"
            )
        
        # Get price history (last 90 days)
        price_history = PredictionService.get_price_history(db, crop_id, market_id, days=90)
        
        if len(price_history) < 7:
            # Not enough data for prediction
            latest_price = price_history[-1] if price_history else None
            if not latest_price:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No price data available for prediction"
                )
            
            return PricePrediction(
                crop_id=crop_id,
                market_id=market_id,
                predicted_price=float(latest_price.price),
                predicted_date=date.today() + timedelta(days=days_ahead),
                confidence=0.3,
                trend="stable",
                trend_percentage=0.0,
                recommendation="Insufficient data for accurate prediction. Current price: {:.2f} ETB".format(
                    float(latest_price.price)
                )
            )
        
        # Extract price values
        price_values = [float(p.price) for p in price_history]
        
        # Calculate moving averages
        ma_7 = PredictionService.calculate_moving_average(price_values, window=7)
        ma_14 = PredictionService.calculate_moving_average(price_values, window=14)
        ma_30 = PredictionService.calculate_moving_average(price_values, window=30)
        
        # Calculate regression
        regression = PredictionService.calculate_simple_regression(price_values)
        slope = regression["slope"]
        intercept = regression["intercept"]
        
        # Predict future price using regression
        future_index = len(price_values) + days_ahead - 1
        predicted_price = slope * future_index + intercept
        
        # Ensure predicted price is positive
        if predicted_price < 0:
            predicted_price = price_values[-1]
        
        # Calculate trend
        current_price = price_values[-1]
        price_change = predicted_price - current_price
        trend_percentage = (price_change / current_price * 100) if current_price > 0 else 0.0
        
        if trend_percentage > 2:
            trend = "rising"
            recommendation = f"Price is expected to rise by {trend_percentage:.1f}% in {days_ahead} days. Consider waiting to sell."
        elif trend_percentage < -2:
            trend = "falling"
            recommendation = f"Price is expected to fall by {abs(trend_percentage):.1f}% in {days_ahead} days. Consider selling soon."
        else:
            trend = "stable"
            recommendation = f"Price is expected to remain relatively stable. Current price: {current_price:.2f} ETB"
        
        # Calculate confidence based on data quality
        data_points = len(price_history)
        confidence = min(0.95, 0.5 + (data_points / 90) * 0.45)
        
        # Adjust confidence based on price volatility
        if len(price_values) >= 7:
            recent_std = PredictionService._calculate_std(price_values[-7:])
            avg_price = sum(price_values[-7:]) / 7
            if avg_price > 0:
                coefficient_of_variation = recent_std / avg_price
                # Lower confidence for high volatility
                if coefficient_of_variation > 0.2:
                    confidence *= 0.8
        
        return PricePrediction(
            crop_id=crop_id,
            market_id=market_id,
            predicted_price=round(predicted_price, 2),
            predicted_date=date.today() + timedelta(days=days_ahead),
            confidence=round(confidence, 2),
            trend=trend,
            trend_percentage=round(trend_percentage, 2),
            recommendation=recommendation
        )
    
    @staticmethod
    def _calculate_std(values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    @staticmethod
    def get_best_time_to_sell(
        db: Session,
        crop_id: int,
        market_id: int
    ) -> BestTimeToSell:
        """
        Get recommendation for best time to sell.
        
        Args:
            db: Database session
            crop_id: Crop ID
            market_id: Market ID
            
        Returns:
            BestTimeToSell object with recommendation
        """
        # Get current price
        latest_statement = (
            select(Price)
            .where(
                Price.crop_id == crop_id,
                Price.market_id == market_id
            )
            .order_by(Price.price_date.desc())
            .limit(1)
        )
        latest_price = db.exec(latest_statement).first()
        
        if not latest_price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No price data available"
            )
        
        current_price = float(latest_price.price)
        
        # Get crop and market details
        crop = db.get(Crop, crop_id)
        market = db.get(Market, market_id)
        
        if not crop or not market:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crop or market not found"
            )
        
        # Get price history for analysis
        price_history = PredictionService.get_price_history(db, crop_id, market_id, days=60)
        
        if len(price_history) < 14:
            # Not enough data
            return BestTimeToSell(
                crop_id=crop_id,
                market_id=market_id,
                crop_name=crop.name,
                market_name=market.name,
                current_price=current_price,
                recommended_price=current_price,
                recommendation="Limited price history available. Current price is {:.2f} ETB. Monitor prices regularly for better timing.".format(
                    current_price
                ),
                confidence=0.4,
                reasoning="Insufficient historical data for detailed analysis"
            )
        
        # Analyze price trends
        price_values = [float(p.price) for p in price_history]
        
        # Calculate short-term and long-term trends
        ma_7 = PredictionService.calculate_moving_average(price_values, window=7)
        ma_14 = PredictionService.calculate_moving_average(price_values, window=14)
        ma_30 = PredictionService.calculate_moving_average(price_values, window=30)
        
        # Find maximum price in history
        max_price = max(price_values)
        max_price_date = None
        for p in price_history:
            if float(p.price) == max_price:
                max_price_date = p.price_date
                break
        
        # Calculate price position relative to historical range
        min_price = min(price_values)
        price_range = max_price - min_price
        price_position = (current_price - min_price) / price_range if price_range > 0 else 0.5
        
        # Generate recommendation
        confidence = 0.7
        
        if current_price >= max_price * 0.95:
            # Price is near historical high
            recommendation = (
                f"Good time to sell! Current price ({current_price:.2f} ETB) is near the "
                f"historical high ({max_price:.2f} ETB). Consider selling now to maximize profit."
            )
            recommended_price = current_price
            confidence = 0.85
            reasoning = "Price is at or near historical maximum"
        
        elif ma_7 > ma_14 > ma_30:
            # Strong upward trend
            recommendation = (
                f"Price is rising steadily. Current: {current_price:.2f} ETB. "
                f"7-day average: {ma_7:.2f} ETB. Consider waiting 3-5 days for potentially higher prices."
            )
            recommended_price = ma_7 * 1.05  # Optimistic projection
            confidence = 0.75
            reasoning = "Strong upward trend detected"
        
        elif ma_7 < ma_14 < ma_30:
            # Declining trend
            recommendation = (
                f"Price is declining. Current: {current_price:.2f} ETB. "
                f"Consider selling soon before prices drop further. "
                f"Recent average: {ma_7:.2f} ETB."
            )
            recommended_price = current_price
            confidence = 0.8
            reasoning = "Declining trend detected - sell soon"
        
        elif price_position > 0.7:
            # Price is in upper range
            recommendation = (
                f"Price is in the upper range of recent history ({current_price:.2f} ETB). "
                f"Good opportunity to sell. Historical range: {min_price:.2f} - {max_price:.2f} ETB."
            )
            recommended_price = current_price
            confidence = 0.7
            reasoning = "Price is in upper 30% of historical range"
        
        else:
            # Price is in lower range
            recommendation = (
                f"Price is relatively low ({current_price:.2f} ETB). "
                f"Consider waiting for better prices if storage is available. "
                f"Historical range: {min_price:.2f} - {max_price:.2f} ETB."
            )
            recommended_price = max_price * 0.9  # Target 90% of max
            confidence = 0.65
            reasoning = "Price is below optimal selling range"
        
        return BestTimeToSell(
            crop_id=crop_id,
            market_id=market_id,
            crop_name=crop.name,
            market_name=market.name,
            current_price=round(current_price, 2),
            recommended_price=round(recommended_price, 2),
            recommendation=recommendation,
            confidence=round(confidence, 2),
            reasoning=reasoning
        )
