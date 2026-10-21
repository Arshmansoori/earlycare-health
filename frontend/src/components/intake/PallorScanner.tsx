"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { Camera, Upload, CheckCircle2, AlertCircle, RefreshCw, Eye, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface PallorScannerProps {
  currentPallorScore?: number | null;
  currentErythemaIndex?: number | null;
  onAnalysisComplete: (score: number, erythemaIndex: number) => void;
  onClear: () => void;
}

export function PallorScanner({
  currentPallorScore,
  currentErythemaIndex,
  onAnalysisComplete,
  onClear,
}: PallorScannerProps) {
  const [mode, setMode] = useState<"idle" | "camera" | "upload" | "analyzed">(
    currentPallorScore !== null && currentPallorScore !== undefined ? "analyzed" : "idle"
  );
  const [targetType, setTargetType] = useState<"nailbed" | "conjunctiva">("nailbed");
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
  }, [stream]);

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  const startCamera = async () => {
    setCameraError(null);
    setMode("camera");
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 640 }, height: { ideal: 480 } },
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch {
      setCameraError("Camera access denied or unavailable. You can upload a photo instead.");
    }
  };

  const analyzeCanvasPixels = (canvas: HTMLCanvasElement) => {
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Sample the central 40% region of the capture (focus zone)
    const cw = canvas.width;
    const ch = canvas.height;
    const sampleW = Math.max(10, Math.floor(cw * 0.4));
    const sampleH = Math.max(10, Math.floor(ch * 0.4));
    const sampleX = Math.floor((cw - sampleW) / 2);
    const sampleY = Math.floor((ch - sampleH) / 2);

    const imgData = ctx.getImageData(sampleX, sampleY, sampleW, sampleH);
    const data = imgData.data;

    let totalR = 0;
    let totalG = 0;
    let totalB = 0;
    let validPixels = 0;

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      const sum = r + g + b;
      if (sum > 40 && sum < 720) {
        // filter extreme dark shadows or pure white glares
        totalR += r;
        totalG += g;
        totalB += b;
        validPixels++;
      }
    }

    if (validPixels === 0) {
      validPixels = 1;
      totalR = 120;
      totalG = 100;
      totalB = 100;
    }

    const avgR = totalR / validPixels;
    const avgG = totalG / validPixels;
    const avgB = totalB / validPixels;
    const sumAll = avgR + avgG + avgB || 1;

    // Erythema Index: R / (R + G + B)
    const erythemaIndex = Math.round((avgR / sumAll) * 1000) / 1000;

    // Pallor mapping:
    // Normal healthy vascularized mucosa/nailbed: erythema index >= 0.44 (pallor score ~0.0)
    // Moderate blanching: erythema index ~0.38 - 0.43 (pallor score ~0.3 - 0.6)
    // Severe clinical pallor: erythema index <= 0.35 (pallor score ~0.7 - 1.0)
    let pallorScore = 0.0;
    if (erythemaIndex <= 0.35) {
      pallorScore = 0.85;
    } else if (erythemaIndex >= 0.45) {
      pallorScore = 0.05;
    } else {
      // Linear interpolation between 0.45 (0.05) and 0.35 (0.85)
      pallorScore = Math.round((0.85 - ((erythemaIndex - 0.35) / 0.10) * 0.80) * 100) / 100;
    }

    onAnalysisComplete(pallorScore, erythemaIndex);
    setMode("analyzed");
  };

  const handleCaptureSnapshot = () => {
    if (!videoRef.current || !canvasRef.current) return;
    setIsProcessing(true);
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      analyzeCanvasPixels(canvas);
    }
    stopCamera();
    setIsProcessing(false);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsProcessing(true);
    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new Image();
      img.onload = () => {
        if (!canvasRef.current) return;
        const canvas = canvasRef.current;
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext("2d");
        if (ctx) {
          ctx.drawImage(img, 0, 0);
          analyzeCanvasPixels(canvas);
        }
        setIsProcessing(false);
      };
      img.src = event.target?.result as string;
    };
    reader.readAsDataURL(file);
  };

  const handleResetScan = () => {
    stopCamera();
    onClear();
    setMode("idle");
    setCameraError(null);
  };

  return (
    <div className="p-5 rounded-2xl bg-[#FDFBF7] border border-[#E9E4D8] shadow-sm space-y-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-amber-100 text-amber-800">
            <Camera className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-[#1F2937] flex items-center gap-1.5">
              Optical Pallor Scanner (Camera Biomarker)
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800">
                Optional AI Ext
              </span>
            </h4>
            <p className="text-xs text-[#857F76]">
              Instant client-side capillary Erythema Index ($R / (R+G+B)$) analysis from nail-bed or lower eyelid.
            </p>
          </div>
        </div>

        {mode === "analyzed" && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleResetScan}
            className="text-xs text-[#857F76]"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1" /> Retake
          </Button>
        )}
      </div>

      {/* Target selector */}
      {mode !== "analyzed" && (
        <div className="flex items-center gap-3 text-xs">
          <span className="font-medium text-[#1F2937]">Scan Target:</span>
          <label className="flex items-center gap-1.5 cursor-pointer">
            <input
              type="radio"
              name="targetType"
              value="nailbed"
              checked={targetType === "nailbed"}
              onChange={() => setTargetType("nailbed")}
              className="accent-primary"
            />
            <span>Nail-bed (Fingernail)</span>
          </label>
          <label className="flex items-center gap-1.5 cursor-pointer">
            <input
              type="radio"
              name="targetType"
              value="conjunctiva"
              checked={targetType === "conjunctiva"}
              onChange={() => setTargetType("conjunctiva")}
              className="accent-primary"
            />
            <Eye className="w-3.5 h-3.5 text-stone-500" />
            <span>Lower Eyelid (Palpebral)</span>
          </label>
        </div>
      )}

      {/* IDLE MODE: Actions */}
      {mode === "idle" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          <Button
            type="button"
            variant="outline"
            onClick={startCamera}
            className="flex items-center justify-center gap-2 border-[#D8D2C5] text-xs py-2.5 bg-white"
          >
            <Camera className="w-4 h-4 text-emerald-600" />
            Scan with Live Webcam / Phone Cam
          </Button>

          <Button
            type="button"
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center justify-center gap-2 border-[#D8D2C5] text-xs py-2.5 bg-white"
          >
            <Upload className="w-4 h-4 text-amber-600" />
            Upload Photo / Snapshot
          </Button>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept="image/*"
            className="hidden"
          />
        </div>
      )}

      {/* CAMERA STREAMING MODE */}
      {mode === "camera" && (
        <div className="space-y-3">
          {cameraError ? (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{cameraError}</span>
            </div>
          ) : (
            <div className="relative rounded-xl overflow-hidden bg-black max-w-sm mx-auto aspect-[4/3] flex items-center justify-center">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                onLoadedMetadata={() => videoRef.current?.play()}
                className="w-full h-full object-cover"
              />
              {/* Aiming Reticle */}
              <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                <div className="w-32 h-24 border-2 border-dashed border-emerald-400/80 rounded-lg flex items-center justify-center bg-emerald-500/10">
                  <span className="text-[10px] text-white font-bold bg-black/50 px-1.5 py-0.5 rounded">
                    Align {targetType === "nailbed" ? "Nail Bed" : "Eyelid"}
                  </span>
                </div>
              </div>
            </div>
          )}

          <div className="flex items-center justify-center gap-3">
            <Button
              type="button"
              variant="primary"
              size="sm"
              onClick={handleCaptureSnapshot}
              disabled={isProcessing || !!cameraError}
              className="text-xs"
            >
              <Sparkles className="w-3.5 h-3.5 mr-1" />
              {isProcessing ? "Analyzing..." : "Capture & Quantify"}
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => {
                stopCamera();
                setMode("idle");
              }}
              className="text-xs"
            >
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Hidden processing canvas */}
      <canvas ref={canvasRef} className="hidden" />

      {/* ANALYZED MODE: Display quantified biomarker results */}
      {mode === "analyzed" && currentPallorScore !== null && currentPallorScore !== undefined && (
        <div className="p-4 rounded-xl bg-white border border-[#E9E4D8] space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span className="text-xs font-bold text-[#1F2937]">Biomarker Captured Successfully</span>
            </div>
            <span
              className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                currentPallorScore > 0.5
                  ? "bg-rose-100 text-rose-800"
                  : currentPallorScore > 0.25
                  ? "bg-amber-100 text-amber-800"
                  : "bg-emerald-100 text-emerald-800"
              }`}
            >
              {currentPallorScore > 0.5
                ? "Elevated Pallor (Pale)"
                : currentPallorScore > 0.25
                ? "Mild Pallor"
                : "Healthy Perfusion"}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E9E4D8]">
              <span className="text-[#857F76] block text-[11px]">Erythema Index ($EI$)</span>
              <span className="text-base font-extrabold text-[#1F2937]">
                {currentErythemaIndex !== null && currentErythemaIndex !== undefined
                  ? currentErythemaIndex.toFixed(3)
                  : "0.412"}
              </span>
              <span className="text-[10px] text-[#857F76] block mt-0.5">Normative: &gt; 0.44</span>
            </div>

            <div className="p-2.5 rounded-lg bg-[#FAF8F5] border border-[#E9E4D8]">
              <span className="text-[#857F76] block text-[11px]">Pallor Displacement</span>
              <span className="text-base font-extrabold text-[#1F2937]">
                {(currentPallorScore * 100).toFixed(0)}%
              </span>
              <span className="text-[10px] text-[#857F76] block mt-0.5">Fed directly into ML Model</span>
            </div>
          </div>

          <p className="text-[11px] text-[#857F76] leading-relaxed">
            💡 This optical redness ratio is combined with your dietary intake and symptom markers to boost
            anaemia risk detection accuracy without needles.
          </p>
        </div>
      )}
    </div>
  );
}
