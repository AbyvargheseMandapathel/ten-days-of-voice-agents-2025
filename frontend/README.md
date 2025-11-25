# Frontend - Teach-the-Tutor UI

Modern Next.js frontend with smooth animations and professional design.

## Quick Start

```bash
# Install dependencies
pnpm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with LiveKit credentials

# Run development server
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000)

## Environment Variables

Required in `.env.local`:

```bash
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
LIVEKIT_URL=ws://127.0.0.1:7880
```

## Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── (app)/             # Main app routes
│   ├── api/               # API routes
│   └── ui/                # UI components
├── components/
│   ├── app/               # App-specific components
│   └── livekit/           # LiveKit components
├── styles/
│   └── globals.css        # Global styles + animations
└── public/                # Static assets
```

## Features

- **Smooth Animations**: Fade-in, slide-up, float effects
- **Gradient Design**: Modern indigo/purple/pink theme
- **Responsive**: Works on all screen sizes
- **Dark Mode**: Automatic theme switching
- **Real-time Audio**: LiveKit integration

## Tech Stack

- Next.js 15.5.2 (Turbopack)
- React 19.2.0
- TypeScript 5.9.3
- Tailwind CSS 4.1.17
- LiveKit Components React 2.9.16
- Motion (Framer Motion) 12.23.24

## Customization

### Colors

Edit `app-config.ts` to change accent colors:

```typescript
accent: '#6366f1',        // Indigo
accentDark: '#818cf8',    // Light indigo
```

### Animations

Custom animations in `styles/globals.css`:
- `animate-fade-in`
- `animate-slide-up`
- `animate-float`

## Documentation

See the [main README](../README.md) for complete setup instructions.

---

Part of the **Murf AI Voice Agents Challenge - Day 4**
