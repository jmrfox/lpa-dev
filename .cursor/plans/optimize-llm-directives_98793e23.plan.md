---
name: optimize-llm-directives
overview: Optimize LLM directives across .cursor/ and lightning-pose-app/AGENTS.md to establish modern Angular 20/21 best practices, modular architecture, and a collaborative AI-assisted UI design workflow.
todos:
  - id: update-agents-md
    content: Draft and update UI Architecture & Standards in lightning-pose-app/AGENTS.md
    status: completed
  - id: update-angular-rule
    content: Update and modernize .cursor/rules/angular-20.mdc with Angular 20/21 patterns and proper globs
    status: completed
  - id: refine-lpa-ui-components
    content: Refine .cursor/rules/lpa-ui-components.mdc for DaisyUI 5 and component structure
    status: completed
  - id: create-ui-workflow-rule
    content: Create .cursor/rules/ui-workflow.mdc for AI collaboration, modular scaffolding, and frontend advisory
    status: completed
  - id: verify-directives
    content: Review and verify all modified directives
    status: completed
isProject: false
---

# Plan: Optimize LLM Directives for Lightning Pose App UI Development

## Overview & Boundary Separation
To support your dev loop (designing changes, describing them to the AI, and having the AI write modular, maintainable, modern code) while learning frontend development:
- **Public Repo (`lightning-pose-app/AGENTS.md`)**: Public-facing standards applicable to any developer or AI working on LPA. Upgrades the raw link dump into a concrete, actionable **UI Architecture & Angular Standards Guide** (signals, standalone, OnPush, `@ngrx/signals`, DaisyUI 5, testing).
- **Studio / User Workspace (`.cursor/rules/`)**: Studio-specific and developer-specific rules. Enhances `.cursor/rules/angular-20.mdc`, refines `.cursor/rules/lpa-ui-components.mdc`, and introduces a new workflow rule `.cursor/rules/ui-workflow.mdc` that instructs the AI to act as a frontend architecture advisor, explain modern patterns, propose modular breakdowns before implementing, and enforce tests and stories.

---

## 1. Public Repo: Modernize `lightning-pose-app/AGENTS.md`
**File:** [lightning-pose-app/AGENTS.md](lightning-pose-app/AGENTS.md)

Replace the 140 lines of raw external URLs under `# Angular llms.txt` with a comprehensive **UI Architecture & Modern Angular Standards** guide, followed by a concise curated reference table to official resources.

### Key Sections to Add/Expand:
- **Architecture & Component Boundaries**:
  - **Smart (Container) Components**: Live in feature directories (e.g. `web_ui/src/app/viewer/`, `labeler/`, `video-player/`). Manage feature state, coordinate with `SessionService` and `RpcService`, and pass state down.
  - **Dumb (Presentational) Components**: Small, reusable UI elements live in `web_ui/src/app/components/`. Pure inputs and outputs (`input()`, `output()`, `model()`), no direct backend service injection. Must have companion `*.stories.ts`.
  - **Single Responsibility & Collocation**: Keep components small and focused. Collocate `*.component.ts`, `*.component.html`, `*.spec.ts`, and `*.stories.ts`.
- **Modern Angular Reactivity (v20/21)**:
  - `ChangeDetectionStrategy.OnPush` on every component.
  - Signal Inputs & Outputs: `input()`, `input.required()`, `output()`.
  - Two-way Signal Bindings: `model()` instead of paired `@Input()` / `@Output()`.
  - Signal Queries: `viewChild()` / `viewChildren()` instead of `@ViewChild`.
  - Derived & Dynamic State: `computed()` for pure derivations; `linkedSignal()` for state that syncs with an input or signal but is locally writable.
  - State Mutation: Always use `update()` or `set()`. Never mutate objects in place.
- **Modern Templates & Control Flow**:
  - Native control flow: `@if`, `@for (item of items; track item.id)`, `@switch`.
  - Template local variables: `@let` syntax for avoiding repeated signal reads or complex template expressions.
  - Styling bindings: Native `[class.active]="..."` and `[style.width.px]="..."`. Avoid legacy `ngClass` and `ngStyle`.
- **State Management Stack**:
  - Simple local state: Angular `signal()` and `computed()`.
  - Complex feature/multi-signal state: `@ngrx/signals` (`signalStore` or `signalState`) or dedicated `@Injectable()` service.
  - Event streaming: RxJS `Subject` / `BehaviorSubject` for async event-driven pipelines; interop via `toSignal()` / `toObservable()`.
- **Styling Standards**:
  - DaisyUI 5 (`dim` theme) utility-first classes (`btn`, `input`, `range`, `badge`, `modal`).
  - Tailwind 4 layout utilities.
  - Explicit exceptions: custom `.jump-field` in Viewer where DaisyUI `input` is too tall.
- **Testing & Quality Assurance**:
  - Collocated unit tests (`*.spec.ts`) asserting user interactions (accessible roles, `aria-label`, click events).
  - Use `fixture.componentRef.setInput(...)` for testing signal inputs.
  - Mandatory mocks for `ProjectInfoService` and `RpcService`.
  - Storybook stories for visual feedback and documentation.
- **Curated Official References**:
  - Keep a streamlined reference pointing to `https://angular.dev` and `https://angular.dev/assets/context/llms-full.txt`.

---

## 2. Studio / Workspace: Modernize `.cursor/rules/angular-20.mdc`
**File:** [.cursor/rules/angular-20.mdc](.cursor/rules/angular-20.mdc)

Update and refine the rule to cover Angular 20/21 features and proper glob targeting:
- **Globs**: Explicitly scope to `lightning-pose-app/web_ui/**/*.{html,css,ts}` so it triggers during frontend work without cluttering Python backend prompts.
- **OnPush Change Detection**: Require `ChangeDetectionStrategy.OnPush` as standard.
- **Signal Two-Way Bindings**: Add `model()` pattern with clear Good/Bad examples.
- **Signal Queries**: Add `viewChild()` / `viewChildren()` syntax.
- **Template Variables**: Add `@let` syntax examples.
- **Signal Derivations**: Add `linkedSignal()` pattern for writable derived inputs.
- **Testing Patterns**: Add signal component testing conventions (`componentRef.setInput`).

---

## 3. Studio / Workspace: Refine `.cursor/rules/lpa-ui-components.mdc`
**File:** [.cursor/rules/lpa-ui-components.mdc](.cursor/rules/lpa-ui-components.mdc)

- Align with DaisyUI 5 and Tailwind CSS 4 guidelines.
- Clarify the separation between reusable widgets in `web_ui/src/app/components/` (with Storybook stories) and domain-specific UI in feature directories.

---

## 4. Studio / Workspace: Add Developer Workflow Rule `.cursor/rules/ui-workflow.mdc`
**File:** Create `.cursor/rules/ui-workflow.mdc`

Add a dedicated rule tailored to Jordan's dev loop and learning journey:
- **Role as Frontend Architecture Advisor**:
  - When the user describes a planned UI feature or change, the AI must first suggest the modular breakdown (Smart container vs Dumb presentational components, signal/store design, DaisyUI primitives).
  - Briefly explain the "why" behind modern frontend choices (e.g. why OnPush + Signals ensures zoneless performance, why `model()` eliminates boilerplate, why Dumb components shouldn't touch backend services).
- **Modularity & Scaffolding Principles**:
  - Keep components small and focused on a single responsibility.
  - Define clear TypeScript models and view interfaces before writing template code.
  - Collocate tests (`*.spec.ts`) and stories (`*.stories.ts`) with every new component.
- **Safe Dev Loop Checklist**:
  - 1. Design & Component breakdown proposal (user review).
  - 2. Write modular component + template.
  - 3. Add/update unit test asserting user interactions.
  - 4. Add/update Storybook story.
  - 5. Verify with `npx ng lint` and targeted test.

---

## 5. Verification & Review
- Verify markdown rendering and formatting across modified files.
- Ensure strict separation between public guidance (`lightning-pose-app/AGENTS.md`) and studio-specific guidance (`.cursor/rules/`).
- Leave working tree clean for user review (no git commit or push, per workspace rules).