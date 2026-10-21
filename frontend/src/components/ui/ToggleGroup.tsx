// frontend/src/components/ui/ToggleGroup.tsx
import React from "react";

export interface ToggleOption<T extends string | boolean | number> {
  value: T;
  label: string;
  sublabel?: string;
  icon?: React.ReactNode;
}

interface ToggleGroupProps<T extends string | boolean | number> {
  label?: string;
  helperText?: string;
  options: ToggleOption<T>[];
  value: T;
  onChange: (val: T) => void;
  className?: string;
  columns?: 2 | 3 | 4;
}

export function ToggleGroup<T extends string | boolean | number>({
  label,
  helperText,
  options,
  value,
  onChange,
  className = "",
  columns,
}: ToggleGroupProps<T>) {
  const gridClasses = {
    2: "grid-cols-2",
    3: "grid-cols-3",
    4: "grid-cols-2 sm:grid-cols-4",
  };

  const layoutClass = columns
    ? `grid gap-2 ${gridClasses[columns]}`
    : "flex flex-wrap gap-2";

  return (
    <div className={`space-y-1.5 ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-[#1F2937]">
          {label}
        </label>
      )}
      {helperText && (
        <p className="text-xs text-[#6B7280]">{helperText}</p>
      )}

      <div className={layoutClass}>
        {options.map((opt) => {
          const isSelected = opt.value === value;
          return (
            <button
              key={String(opt.value)}
              type="button"
              onClick={() => onChange(opt.value)}
              className={`flex flex-col items-center justify-center p-3 text-center rounded-xl border text-xs font-medium transition-all duration-150 cursor-pointer ${
                isSelected
                  ? "bg-[#1F2937] text-white border-[#1F2937] shadow-sm"
                  : "bg-white text-[#1F2937] border-[#E9E4D8] hover:border-[#D8D1C3] hover:bg-[#FAF8F5]"
              }`}
            >
              {opt.icon && <span className="mb-1 text-base">{opt.icon}</span>}
              <span className="font-semibold">{opt.label}</span>
              {opt.sublabel && (
                <span
                  className={`text-[10px] mt-0.5 ${
                    isSelected ? "text-stone-300" : "text-[#857F76]"
                  }`}
                >
                  {opt.sublabel}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
