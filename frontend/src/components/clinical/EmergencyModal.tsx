// frontend/src/components/clinical/EmergencyModal.tsx
import React from "react";
import { AlertTriangle, PhoneCall, Hospital, XCircle } from "lucide-react";
import { Modal } from "../ui/Modal";
import { Button } from "../ui/Button";

interface EmergencyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const EmergencyModal: React.FC<EmergencyModalProps> = ({ isOpen, onClose }) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Immediate Medical Evaluation Recommended"
      subtitle="Critical Red-Flag Symptom Detected"
      maxWidth="lg"
    >
      <div className="space-y-4">
        <div className="p-4 bg-[#FEF2F2] rounded-2xl border border-[#FECACA] flex items-start gap-3">
          <div className="p-2 bg-[#EF4444] text-white rounded-xl shadow-sm shrink-0">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-[#991B1B]">
              Do Not Proceed with Routine Online Screening
            </h4>
            <p className="text-xs text-[#7F1D1D] mt-1 leading-relaxed">
              You reported acute chest pain, unexplained fainting (syncope), or active bleeding. These indicators represent potential acute cardiovascular or hemodynamic emergencies that require immediate, in-person clinical assessment by emergency medical personnel.
            </p>
          </div>
        </div>

        <div className="space-y-3">
          <h5 className="text-xs font-bold uppercase tracking-wider text-[#1F2937]">
            Urgent Campus & Emergency Resources:
          </h5>

          <div className="grid gap-2.5 sm:grid-cols-2">
            <a
              href="tel:911"
              className="flex items-center gap-3 p-3 bg-white rounded-xl border border-[#E9E4D8] hover:border-[#EF4444] hover:bg-[#FEF2F2]/30 transition-all group shadow-sm"
            >
              <div className="p-2 rounded-lg bg-rose-100 text-[#DC2626] group-hover:scale-105 transition-transform">
                <PhoneCall className="w-5 h-5" />
              </div>
              <div>
                <span className="block text-xs font-bold text-[#1F2937]">
                  Emergency Services
                </span>
                <span className="block text-[11px] text-[#DC2626] font-semibold">
                  Dial 911 (Immediate)
                </span>
              </div>
            </a>

            <div className="flex items-center gap-3 p-3 bg-white rounded-xl border border-[#E9E4D8] shadow-sm">
              <div className="p-2 rounded-lg bg-amber-100 text-[#D97706]">
                <Hospital className="w-5 h-5" />
              </div>
              <div>
                <span className="block text-xs font-bold text-[#1F2937]">
                  Campus Student Health
                </span>
                <span className="block text-[11px] text-[#6B7280]">
                  Walk-in Urgent Care Clinic
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="p-3 bg-[#F8F6F0] rounded-xl border border-[#E9E4D8] text-[11px] text-[#6B7280]">
          <strong>Protocol Notice:</strong> EarlyCare has halted routine wellness calculations for this session. Please prioritize your physical safety and seek clinical care right away.
        </div>

        <div className="pt-3 border-t border-[#E9E4D8] flex justify-end gap-2">
          <Button
            variant="outline"
            onClick={onClose}
            className="text-xs"
          >
            <XCircle className="w-4 h-4 mr-1.5" /> Close Alert
          </Button>
          <a href="tel:911" className="inline-block">
            <Button variant="danger" className="text-xs">
              <PhoneCall className="w-4 h-4 mr-1.5" /> Call Emergency 911
            </Button>
          </a>
        </div>
      </div>
    </Modal>
  );
};
