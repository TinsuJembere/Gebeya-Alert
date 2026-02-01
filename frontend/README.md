# GebeyaAlert Frontend

Next.js frontend for GebeyaAlert - Price Alerts for Farmers.

## Features

- Mobile-first responsive design
- JWT authentication
- Tailwind CSS styling
- TypeScript support
- App Router (Next.js 14)

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
npm install
# or
yarn install
```

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/        # React components
│   ├── contexts/          # React contexts (Auth, etc.)
│   ├── lib/               # Utilities and API client
│   └── utils/             # Helper functions
├── public/                # Static assets
└── package.json
```

## Features

- **Authentication**: JWT-based auth with phone number login
- **API Client**: Axios-based client with automatic token injection
- **Mobile-First**: Responsive design optimized for mobile devices
- **TypeScript**: Full type safety
















