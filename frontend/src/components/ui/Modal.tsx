// frontend/src/components/ui/Modal.tsx
import React, { useEffect } from "react";
import { X } from "lucide-react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl" | "4xl";
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  maxWidth = "lg",
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      document.body.style.overflow = "unset";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const widthClasses = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    "2xl": "max-w-2xl",
    "4xl": "max-w-4xl",
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      className="fixed inset-0 z-50 overflow-y-auto bg-black/40 backdrop-blur-sm flex items-center justify-center p-4"
    >
      <div
        className="fixed inset-0 transition-opacity"
        aria-hidden="true"
        onClick={onClose}
      />

      <div
        className={`relative w-full ${widthClasses[maxWidth]} bg-white rounded-3xl shadow-warm-lg border border-[#E9E4D8] overflow-hidden transform transition-all p-6 my-8 z-10`}
      >
        <div className="flex items-start justify-between pb-4 border-b border-[#E9E4D8]">
          <div>
            <h2 id="modal-title" className="text-xl font-bold text-[#1F2937]">
              {title}
            </h2>
            {subtitle && (
              <p className="text-xs text-[#6B7280] mt-1">{subtitle}</p>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close dialog"
            className="p-1.5 rounded-full text-[#6B7280] hover:text-[#1F2937] hover:bg-[#F5F0E8] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mt-4 max-h-[75vh] overflow-y-auto pr-1">
          {children}
        </div>
      </div>
    </div>
  );
};
