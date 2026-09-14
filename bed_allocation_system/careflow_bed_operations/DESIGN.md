---
name: CareFlow Bed Operations
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e4e2e1'
  on-surface: '#1b1c1c'
  on-surface-variant: '#574144'
  inverse-surface: '#303030'
  inverse-on-surface: '#f3f0ef'
  outline: '#8b7174'
  outline-variant: '#debfc2'
  surface-tint: '#ac2d50'
  primary: '#a92a4d'
  on-primary: '#ffffff'
  primary-container: '#ca4465'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb2be'
  secondary: '#aa3050'
  on-secondary: '#ffffff'
  secondary-container: '#fd6f8e'
  on-secondary-container: '#6f0029'
  tertiary: '#615a5c'
  on-tertiary: '#ffffff'
  tertiary-container: '#7a7375'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffd9de'
  primary-fixed-dim: '#ffb2be'
  on-primary-fixed: '#400014'
  on-primary-fixed-variant: '#8c1039'
  secondary-fixed: '#ffd9de'
  secondary-fixed-dim: '#ffb2be'
  on-secondary-fixed: '#400014'
  on-secondary-fixed-variant: '#8a153a'
  tertiary-fixed: '#eae0e2'
  tertiary-fixed-dim: '#cdc4c6'
  on-tertiary-fixed: '#1f1a1c'
  on-tertiary-fixed-variant: '#4b4547'
  background: '#fcf9f8'
  on-background: '#1b1c1c'
  surface-variant: '#e4e2e1'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
  metric-tabular:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '700'
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 0.75rem
  gutter-compact: 0.5rem
  margin: 1rem
  margin-panel: 0.75rem
  space-xs: 0.25rem
  space-sm: 0.375rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
---

## Brand & Style

This design system delivers a clinical command center aesthetic engineered for acute hospital triage, bed tracking, and patient throughput operations. The user interface prioritizes clarity, operational speed, and rapid pattern recognition for charge nurses, unit coordinators, and emergency department operations managers working in high-stress, decision-critical environments.

The visual style rejects consumer SaaS decoration, marketing flourishes, and artificial glassmorphism in favor of structured, high-density telemetry. Surfaces are crisp, surgical, and legible from a distance of several feet across unit monitor banks. Restrained color coding ensures that alerts, bed statuses, and acuity indicators convey instant, life-critical meaning without sensory fatigue.

## Colors

The palette is tuned for day-to-day hospital operations under fluorescent clinical lighting, emphasizing structural contrast and immediate semantic distinction.

### Primary & Action Surfaces
- **Primary (`#D94F70`)**: Operational focal color used for primary allocations, primary unit filters, and vital workflow indicators.
- **Primary Dark / Interactive Hover (`#B83A5A`)**: Used for hover states, focused actions, and critical alert borders.
- **Surface Subdued (`#FFF5F7`)**: Tinted clinical blush surface used for active ward zones, assigned bed card backgrounds, and filtered summaries.

### Neutrals & Structure
- **Canvas (`#FFFFFF`)**: Pure surgical white base canvas ensuring maximum data density and stark contrast.
- **Text Primary (`#252525`)**: High-contrast charcoal for patient names, MRNs, bed identifiers, and critical metrics.
- **Text Secondary (`#6B7280`)**: Slate gray for metadata, room labels, elapsed timestamps, and supporting labels.
- **Base Border (`#E5E7EB`)**: Standard structural perimeter for unassigned beds, grid lines, and data tables.
- **Subtle Pink Border (`#FCE7ED`)**: Accented structural perimeter denoting active unit telemetry, pending transfers, and assigned allocations.

### Clinical Status Telemetry
- **Available / Clear (`#10B981`)**: Bed sanitized and available for intake.
- **Warning / Limited / Pending (`#F59E0B`)**: Pending discharge, cleaning underway, or staffing bottlenecks.
- **Critical / Action Required (`#B83A5A` / `#D94F70`)**: Rapid response required, telemetry disconnected, or isolation barrier.

## Typography

The typographic hierarchy prioritizes rapid scannability and absolute numerical precision. All metrics, patient tracking numbers, encounter times, and bed capacities must render using tabular figures (`font-variant-numeric: tabular-nums`) to prevent alignment jitter during real-time updates.

- **Scale**: Compact sizing (ranging primarily from 11px to 16px) accommodates dense grid boards and multi-bed ward telemetry without clipping or horizontal truncation.
- **Hierarchy**: Section heads anchor the layout, while patient IDs, bed codes, and acuity tags utilize semibold labels with slight letter-spacing for split-second identification.
- **Labels**: Acuity level, isolation codes, and status tags employ uppercase `label-sm` weights to distinguish permanent operational metadata from dynamic patient clinical data.

## Layout & Spacing

Layouts follow a high-density, multi-panel operational grid designed for wide clinical workstations, multi-monitor telemetry hubs, and mobile triage tablets.

- **Grid System**: A responsive 12-column layout with tight `0.75rem` (12px) gutters maximizing usable area across bed census dashboards.
- **Panel Rhythms**: Information panels utilize internal margins of `0.75rem` to `1rem`, allowing up to 36 patient bed cards to remain visible above the fold on standard 1080p workstations.
- **Vertical Rhythm**: Micro-spacers (`0.25rem` to `0.375rem`) group related patient vitals, telemetry indicators, and bed state metadata, preventing cognitive fragmentation.
- **Responsive Handling**:
  - **Desktop (1440px+)**: Multi-column ward overview (ED, ICU, Med-Surg) alongside a persistent side panel for incoming bed requests.
  - **Workstation / Tablet (1024px–1439px)**: 2-column ward arrangement with collapsable allocation tray.
  - **Mobile / Cart (below 1024px)**: Single-column high-contrast card list prioritized by pending discharges and critical intake bottlenecks.

## Elevation & Depth

Visual depth is achieved through flat, crisp structural containment rather than heavy drop shadows, preserving an austere, clinical operational feel:

- **Surface Levels**:
  - **Level 0 (Floor Canvas)**: `#FFFFFF` clinical white for overall background.
  - **Level 1 (Bed Cards & Data Panels)**: `#FFFFFF` or `#FFF5F7` framed by a 1px border (`#E5E7EB` or `#FCE7ED`).
  - **Level 2 (Active Drawer / Allocation Drawer)**: `#FFFFFF` overlay bordered by `#E5E7EB` with a functional operational drop shadow: `0 2px 4px rgba(0, 0, 0, 0.06)`.
  - **Level 3 (Emergency Modal / Critical Alert Flyout)**: `0 8px 16px rgba(0, 0, 0, 0.08)`, centered with a solid 2px alert bar in `#B83A5A`.
- **Shadow Principles**: Never use diffuse ambient glows or colored shadows. All shadows must be tight, neutral (`rgba(0, 0, 0, 0.04 - 0.08)`), and strictly functional to separate overlapping modal layers from data tables.

## Shapes

Shapes reflect precision and structural stability. Border radii are tightly constrained to avoid overly playful consumer software aesthetics.

- **Base Radius (0.25rem / 4px)**: Applied to table elements, badges, status chips, form inputs, and buttons.
- **Card & Panel Radius (0.375rem - 0.5rem / 6px - 8px)**: Applied to bed slot containers, modal windows, and ward grouping boxes.
- **Corners**: Strictly uniform. No asymmetric corners or pill containers for functional bed telemetry cards.

## Components

### Bed Telemetry Cards
- **Construction**: 1px solid border in `#E5E7EB` (unoccupied/ready) or `#FCE7ED` (occupied/assigned), background `#FFFFFF` or `#FFF5F7`.
- **Header**: Compact row with bed ID (`Inter 13px bold`), isolation badge if applicable, and quick action icon button.
- **Body**: Patient initials or name, MRN in tabular monospace, assigned attending staff, elapsed hours since admission.
- **Footer**: Status chip (Cleaning, Available, Occupied, Blocked) anchored to bottom right with 4px corner radius.

### Buttons
- **Primary Action**: Solid `#D94F70` background, `#FFFFFF` text, `0.25rem` radius, hover `#B83A5A`. Active states depress by 1px without heavy transition animation.
- **Secondary / Operational**: Background `#FFFFFF`, 1px solid `#E5E7EB`, text `#252525`, hover background `#FFF5F7` and border `#FCE7ED`.
- **Critical Alert**: Solid `#B83A5A` background, `#FFFFFF` text, used exclusively for escalation workflows and bypass transfers.

### Status Chips & Badges
- **Occupied / Clinical Active**: Subtle `#FFF5F7` fill, 1px `#FCE7ED` border, `#B83A5A` text.
- **Ready / Sanitized**: Subtle `#ECFDF5` fill, 1px `#A7F3D0` border, `#065F46` text.
- **Delayed / Pending Discharge**: Subtle `#FFFBEB` fill, 1px `#FDE68A` border, `#92400E` text.
- **Isolation / Alert**: Subtle `#FEF2F2` fill, 1px `#FECACA` border, `#991B1B` text.

### Input Fields & Selects
- **Height**: 32px or 36px dense form controls with 4px border radius.
- **States**: Default border `#E5E7EB`, active/focused border `#D94F70` with 1px outline ring in `#FCE7ED`. Text rendered in `#252525`.

### Data Tables & Roster Lists
- **Rows**: Alternating subtle white and `#FAFAFA` rows with 1px `#E5E7EB` dividing lines.
- **Header**: High-density 28px height, `#6B7280` text in `label-sm` typography, solid `#F9FAFB` fill.
- **Numbers**: Right-aligned, tabular figures enabled for census counts, wait times, and bed turnover durations.