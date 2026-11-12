import { useEffect, useState } from "react";

type Props = {
  label: string;
  options: string[];
  value: string | null;
  disabled?: boolean;
  onPick?: (option: string) => void;
};

// One button per option. Python owns the value; the local copy only shows a click before the rerun.
export function Widget({ label, options, value, disabled, onPick }: Props) {
  const [picked, setPicked] = useState(value);
  useEffect(() => setPicked(value), [value]);

  if (!options.length) return <p className="note">No options to show.</p>;
  return (
    <fieldset className="widget" disabled={disabled || !onPick}>
      <legend>{label}</legend>
      {options.map((o) => (
        <button
          key={o}
          type="button"
          aria-pressed={o === picked}
          onClick={() => {
            setPicked(o);
            onPick?.(o);
          }}
        >
          {o}
        </button>
      ))}
    </fieldset>
  );
}
