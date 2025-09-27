# Frontend CSS Style Guide

This document outlines the standardized CSS architecture and design system for the frontend application.

## Architecture Overview

The CSS is organized into the following structure:

```
src/
├── styles/
│   ├── variables.css    # Design system variables
│   └── base.css         # Base styles and utility classes
├── index.css           # Global imports
├── App.css             # App-specific styles
└── components/
    ├── Component.module.css  # Component-specific styles
    └── ...
```

## Design System

### CSS Custom Properties

All styles use CSS custom properties (CSS variables) defined in `styles/variables.css`:

#### Colors
- **Primary**: `--color-primary` (#4a90e2)
- **Text**: `--color-text-primary`, `--color-text-secondary`, `--color-text-tertiary`
- **Background**: `--color-background-primary`, `--color-background-secondary`, `--color-background-card`
- **Border**: `--color-border-primary`, `--color-border-secondary`, `--color-border-focus`
- **Button**: `--color-button-secondary`, `--color-button-disabled`

#### Typography
- **Font Families**: `--font-family-primary`, `--font-family-secondary`, `--font-family-mono`
- **Font Sizes**: `--font-size-xs` to `--font-size-3xl`
- **Font Weights**: `--font-weight-normal`, `--font-weight-medium`, `--font-weight-semibold`, `--font-weight-bold`
- **Line Heights**: `--line-height-tight`, `--line-height-normal`, `--line-height-relaxed`

#### Spacing
- **Scale**: `--spacing-xs` (0.25rem) to `--spacing-3xl` (3rem)
- **Content**: `--content-padding` for main content areas

#### Border Radius
- **Scale**: `--radius-xs` (2px) to `--radius-xl` (16px)

#### Box Shadows
- **Scale**: `--shadow-xs` to `--shadow-lg`
- **Inset**: `--shadow-inset-sm`, `--shadow-inset-base`

#### Focus Styles
- **Ring**: `--focus-ring`, `--focus-ring-sm`, `--focus-ring-md`

#### Transitions
- **Duration**: `--transition-fast`, `--transition-base`, `--transition-slow`

### Utility Classes

Base utility classes are available in `base.css`:

- **Layout**: `.flex`, `.flex-col`, `.items-center`, `.justify-between`
- **Spacing**: `.gap-sm`, `.gap-md`, `.gap-base`, `.gap-lg`
- **Components**: `.card`, `.btn`, `.btn-primary`, `.btn-secondary`
- **Form Elements**: `.input`, `.select`, `.textarea`

## Component CSS Guidelines

### File Structure
- Use CSS Modules (`.module.css` extension)
- Import variables at the top: `@import '../styles/variables.css';`
- Organize styles in logical order: layout → typography → colors → states

### Naming Conventions
- Use camelCase for CSS Module class names
- Use semantic names that describe purpose, not appearance
- Prefix component-specific classes with component name when needed

### Example Structure
```css
@import '../styles/variables.css';

/* Main component container */
.componentName {
  /* Layout properties */
  display: flex;
  flex-direction: column;
  
  /* Spacing */
  padding: var(--spacing-base);
  gap: var(--spacing-sm);
  
  /* Visual */
  background-color: var(--color-background-card);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-base);
  
  /* Animation */
  transition: all var(--transition-base);
}

/* Child elements */
.componentName h2 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

/* State modifiers */
.componentName:hover {
  box-shadow: var(--shadow-md);
}

/* Interactive elements */
.componentName input {
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-base);
  transition: border-color var(--transition-base);
}

.componentName input:focus {
  outline: none;
  border-color: var(--color-border-focus);
  box-shadow: var(--focus-ring);
}
```

## Best Practices

### Do's
- ✅ Always use CSS variables instead of hardcoded values
- ✅ Use semantic class names
- ✅ Follow consistent spacing scale
- ✅ Apply consistent focus styles
- ✅ Use transitions for smooth interactions
- ✅ Group related properties together
- ✅ Import variables in each component CSS file

### Don'ts
- ❌ Don't use hardcoded colors, sizes, or spacing
- ❌ Don't use `!important` unless absolutely necessary
- ❌ Don't create overly specific selectors
- ❌ Don't mix naming conventions within a file
- ❌ Don't forget focus states for interactive elements

## Form Elements

All form elements should use consistent styles:

```css
/* Input fields */
.input {
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-base);
  background-color: var(--color-background-input);
  transition: border-color var(--transition-base);
}

.input:focus {
  outline: none;
  border-color: var(--color-border-focus);
  box-shadow: var(--focus-ring);
}

/* Buttons */
.btn {
  padding: var(--spacing-md) var(--spacing-base);
  border: 1px solid transparent;
  border-radius: var(--radius-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-base);
}
```

## Responsive Design

While not extensively implemented yet, follow these principles:

- Use relative units (rem, em, %) when possible
- Consider mobile-first approach
- Use CSS Grid and Flexbox for layouts
- Test on multiple screen sizes

## Maintenance

When adding new components or updating styles:

1. Check if existing variables can be used
2. Add new variables to `variables.css` if needed
3. Update this style guide with new patterns
4. Ensure consistency across all components
5. Test focus states and accessibility