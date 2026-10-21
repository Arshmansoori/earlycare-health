// frontend/src/components/ui/Button.tsx
import React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  className = "",
  variant = "primary",
  size = "md",
  isLoading = false,
  disabled,
  ...props
}) => {
  const sizeStyles = {
    sm: "px-3 py-1.5 text-xs font-medium rounded-lg",
    md: "px-5 py-2.5 text-sm font-semibold rounded-xl",
    lg: "px-6 py-3.5 text-base font-semibold rounded-xl",
  };

  const variantStyles = {
    primary:
      "bg-[#1F2937] text-white hover:bg-[#111827] active:bg-[#030712] shadow-sm focus:ring-2 focus:ring-[#1F2937] focus:ring-offset-2",
    secondary:
      "bg-[#F5F0E8] text-[#1F2937] hover:bg-[#E9E4D8] active:bg-[#D8D1C3] border border-[#E9E4D8]",
    outline:
      "bg-transparent text-[#1F2937] border border-[#E9E4D8] hover:bg-[#FAF8F5] active:bg-[#F5F0E8]",
    ghost:
      "bg-transparent text-[#6B7280] hover:text-[#1F2937] hover:bg-[#F5F0E8]",
    danger:
      "bg-[#EF4444] text-white hover:bg-[#DC2626] active:bg-[#B91C1C] shadow-sm",
  };

  return (
    <button
      className={`inline-flex items-center justify-center transition-all duration-150 focus:outline-none disabled:opacity-50 disabled:pointer-events-none cursor-pointer ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {children}
    </button>
  );
};
