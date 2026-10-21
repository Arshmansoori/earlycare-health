// frontend/src/components/ui/Slider.tsx
import React from "react";

interface SliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  helperText?: string;
  statusLabel?: string;
  onChange: (val: number) => void;
  className?: string;
}

export const Slider: React.FC<SliderProps> = ({
  label,
  value,
  min,
  max,
  step = 1,
  unit = "",
  helperText,
  statusLabel,
  onChange,
  className = "",
}) => {
  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-[#1F2937]">
          {label}
        </label>
        <div className="flex items-baseline space-x-1.5">
          <span className="text-lg font-bold text-[#1F2937]">{value}</span>
          {unit && <span className="text-xs text-[#6B7280]">{unit}</span>}
          {statusLabel && (
            <span className="ml-2 text-xs font-medium px-2 py-0.5 rounded-full bg-[#F5F0E8] text-[#1F2937] border border-[#E9E4D8]">
              {statusLabel}
            </span>
          )}
        </div>
      </div>

      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-2 bg-[#E9E4D8] rounded-lg appearance-none cursor-pointer accent-[#1F2937] focus:outline-none focus:ring-2 focus:ring-[#1F2937]/20"
      />

      <div className="flex justify-between text-[11px] text-[#857F76]">
        <span>{min} {unit}</span>
        {helperText && <span className="text-center italic">{helperText}</span>}
        <span>{max} {unit}</span>
      </div>
    </div>
  );
};
