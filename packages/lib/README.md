# @teto/lib

Shared React library for Teto applications (Electron Desktop and Next.js Web).

## Features

- 🎨 **UI Components**: Pre-built React components with Tailwind CSS
- 📝 **Schema Validation**: Type-safe validation with Valibot
- 🏗️ **Domain Logic**: Reusable business logic for video editing
- 🔧 **Utilities**: Common utility functions and helpers
- 🎯 **TypeScript**: Fully typed with TypeScript
- ⚡ **Fast Build**: Built with tsdown (Rust-powered bundler)

## Installation

```bash
pnpm add @teto/lib
```

## Usage

### Importing Components

```tsx
import { Button } from "@teto/lib/components/ui";

function App() {
  return (
    <Button variant="primary" size="md">
      Click me
    </Button>
  );
}
```

### Using Schemas

```tsx
import { VideoProjectSchema } from "@teto/lib/schemas";
import * as v from "valibot";

const project = {
  id: "1",
  name: "My Project",
  width: 1920,
  height: 1080,
  fps: 60,
  duration: 100,
};

// Validate
const validated = v.parse(VideoProjectSchema, project);
```

### Utilities

```tsx
import { cn } from "@teto/lib/utils";

// Merge Tailwind CSS classes
const className = cn("px-4 py-2", "bg-blue-500", "hover:bg-blue-600");
```

## Package Structure

```
packages/lib/
├── src/
│   ├── components/       # UI components
│   │   ├── ui/          # Basic UI components
│   │   ├── layout/      # Layout components
│   │   └── feedback/    # Feedback components
│   ├── schemas/         # Valibot schemas
│   ├── domain/          # Domain logic
│   ├── hooks/           # Custom hooks
│   ├── stores/          # State management (valtio)
│   ├── utils/           # Utility functions
│   ├── types/           # Type definitions
│   └── constants/       # Constants
└── dist/                # Built files
```

## Development

### Build

```bash
pnpm build
```

### Watch Mode

```bash
pnpm dev
```

### Test

```bash
pnpm test
```

### Lint

```bash
pnpm lint
```

### Format

```bash
pnpm format
```

## Design Principles

### Environment Independence

- **Include**: UI components, schemas, domain logic, type definitions, utilities
- **Exclude**: Routing, environment-specific APIs (Electron IPC, Server Actions), data fetching

### Next.js and Electron Compatibility

- All interactive components use `'use client'` directive
- Electron ignores `'use client'`, Next.js treats it as Client Component
- Environment-dependent features are defined as abstract interfaces

### Component Patterns

- **Compound Component Pattern**: Basic component design pattern
- **Scoped State Management**: Provider pattern with valtio for component state
- **Global State Management**: Module-level valtio for app-wide state

## Technologies

- **React** 18+
- **TypeScript** 5+
- **Tailwind CSS** 4.1+
- **tsdown**: Rust-powered bundler
- **Valibot**: Lightweight validation library
- **class-variance-authority**: Variant management
- **valtio**: State management
- **Vitest**: Testing framework

## License

MIT
