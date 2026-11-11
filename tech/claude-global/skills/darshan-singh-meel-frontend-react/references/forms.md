# Forms

Layout, labels, wording: `darshan-singh-meel-frontend` (one column, labels above, errors say the fix).

## Which approach
| Form | Use |
|---|---|
| A few fields, validate on submit | React 19: `<form action>` + `useActionState` + zod `safeParse` on `FormData` |
| Many fields, field arrays, dependent fields, validate while typing | React Hook Form + `@hookform/resolvers` + zod (`zodResolver(schema)`) |
| One input (search, filter) | controlled `useState`, no form library |

Docs: react.dev/reference/react/useActionState · react-hook-form.com/get-started · zod.dev

## Simple form
```tsx
const schema = z.object({ name: z.string().min(1, "Enter a name"), email: z.email("Enter a valid email") });
type State = { errors: Record<string, string[] | undefined> };

async function save(_prev: State, formData: FormData): Promise<State> {
  const parsed = schema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) return { errors: z.flattenError(parsed.error).fieldErrors };
  await api.createUser(parsed.data);
  return { errors: {} };
}

const [state, action, isPending] = useActionState(save, { errors: {} });
// <form action={action}> … <Button disabled={isPending}>Create user</Button>
```
- Uncontrolled inputs reset after the action; return the submitted values in state (as `defaultValue`) when they must survive an error.
- Zod calls above are v4 syntax; on zod 3 use `z.string().email()` and `error.flatten()`.

## Rules
- **One schema per form**, in `lib/` or next to the form; the type comes from `z.infer`.
- **The server validates again.** Client validation is for speed, never for security.
- Every input has a visible `<label>` (`htmlFor` / library `Label`); a placeholder is not a label.
- Errors: next to the field, linked with `aria-describedby`, field marked `aria-invalid`; focus the first invalid field on submit.
- Use the right input: `type="email"`, `inputMode`, `autoComplete`, native `<select>` / date input before a custom widget.
- Submit: disable while pending, show progress on the button, keep the entered values on failure.
- Destructive submit (delete, overwrite) → confirm dialog that names the thing.
- Don't mirror form values into global state; the form owns them until submit.

## Version flags
- React Hook Form: v7 is the documented stable, a v8 beta exists. Pin the major; check its React 19 notes.
- Zod 4 needs TS 5.5+ with `strict`; with RHF it needs `@hookform/resolvers` 3.10+ and `moduleResolution: bundler`.
