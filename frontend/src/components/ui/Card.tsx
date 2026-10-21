// frontend/src/components/ui/Card.tsx
import React from "react";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
  variant?: "surface" | "warm" | "subtle";
  bordered?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = "",
  variant = "surface",
  bordered = true,
  ...props
}) => {
  const variantStyles = {
    surface: "bg-white",
    warm: "bg-[#F8F6F0]",
    subtle: "bg-[#FBF9F5]",
  };

  const borderStyle = bordered ? "border border-[#E9E4D8] hover:border-[#D8D1C3]" : "";

  return (
    <div
      className={`rounded-2xl transition-all duration-200 shadow-warm ${variantStyles[variant]} ${borderStyle} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = "",
  ...props
}) => (
  <div className={`p-6 pb-3 ${className}`} {...props}>
    {children}
  </div>
);

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = "",
  ...props
}) => (
  <div className={`p-6 pt-0 ${className}`} {...props}>
    {children}
  </div>
);

export const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = "",
  ...props
}) => (
  <div className={`p-6 pt-3 border-t border-[#E9E4D8] ${className}`} {...props}>
    {children}
  </div>
);
