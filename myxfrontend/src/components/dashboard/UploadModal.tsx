import { useState } from "react";
import { X, Check, Upload, Trash2, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { getCurrentUserName } from "@/lib/auth";

const banks = [
  { name: "OPay", color: "#00C853" },
  { name: "Moniepoint", color: "#1a2e6e" },
  { name: "GTBank", color: "#e85d04" },
  { name: "Ecobank", color: "#0066b2" },
  { name: "Zenith Bank", color: "#e41b23" },
];

const processingSteps = [
  "Reading your statement...",
  "Extracting transactions...",
  "Categorising spending...",
  "Generating insights...",
];

interface UploadModalProps {
  open: boolean;
  onClose: () => void;
  onProcessed?: () => void | Promise<void>;
}

export function UploadModal({ open, onClose, onProcessed }: UploadModalProps) {
  const [step, setStep] = useState(1);
  const [selectedBank, setSelectedBank] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [processStep, setProcessStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  const handleNext = async () => {
    if (step === 1 && selectedBank) setStep(2);
    else if (step === 2 && file && selectedBank) {
      setStep(3);
      setProcessing(true);
      setError(null);

      // Start progress animation
      let p = 0;
      let s = 0;
      const interval = setInterval(() => {
        p += 1;
        if (p <= 90) setProgress(p);
        if (p % 25 === 0 && s < 2) {
          s++;
          setProcessStep(s);
        }
      }, 80);

      try {
        const userName = getCurrentUserName();
        await api.uploadBankStatement(file, userName, selectedBank);
        await onProcessed?.();

        // Complete the progress bar
        clearInterval(interval);
        setProgress(100);
        setProcessStep(3);

        setTimeout(() => {
          setProcessing(false);
          resetAndClose();
        }, 800);
      } catch (err) {
        clearInterval(interval);
        setProcessing(false);
        setError(err instanceof Error ? err.message : "Upload failed. Please try again.");
      }
    }
  };

  const resetAndClose = () => {
    setStep(1);
    setSelectedBank(null);
    setFile(null);
    setProcessing(false);
    setProcessStep(0);
    setProgress(0);
    setError(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="bg-card border border-border rounded-xl shadow-xl w-full max-w-lg mx-4 relative">
        <button onClick={resetAndClose} className="absolute top-4 right-4 text-muted-foreground hover:text-foreground transition-colors">
          <X className="h-5 w-5" />
        </button>

        <div className="p-6">
          {step === 1 && (
            <>
              <p className="text-xs text-muted-foreground mb-1">Step 1 of 2</p>
              <h3 className="text-lg font-bold text-card-foreground mb-4">Select your bank</h3>
              <div className="grid grid-cols-2 gap-3">
                {banks.map((bank) => (
                  <button
                    key={bank.name}
                    onClick={() => setSelectedBank(bank.name)}
                    className={`relative p-4 rounded-lg border text-sm font-medium text-card-foreground transition-all duration-150 ${
                      selectedBank === bank.name
                        ? "border-primary bg-primary/5"
                        : "border-border hover:border-primary/50"
                    }`}
                  >
                    {bank.name}
                    {selectedBank === bank.name && (
                      <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-primary flex items-center justify-center">
                        <Check className="h-3 w-3 text-primary-foreground" />
                      </div>
                    )}
                  </button>
                ))}
              </div>
              <Button onClick={handleNext} disabled={!selectedBank} className="w-full mt-6 bg-primary text-primary-foreground">
                Continue
              </Button>
            </>
          )}

          {step === 2 && (
            <>
              <p className="text-xs text-muted-foreground mb-1">Step 2 of 2</p>
              <h3 className="text-lg font-bold text-card-foreground mb-4">Upload your statement</h3>
              {!file ? (
                <label className="flex flex-col items-center justify-center border-2 border-dashed border-border hover:border-primary rounded-lg p-10 cursor-pointer transition-colors duration-150">
                  <Upload className="h-8 w-8 text-muted-foreground mb-2" />
                  <span className="text-sm text-muted-foreground">Click to upload PDF, CSV, or Excel</span>
                  <input type="file" accept=".pdf,.csv,.xlsx,.xls" className="hidden" onChange={(e) => setFile(e.target.files?.[0] || null)} />
                </label>
              ) : (
                <div className="flex items-center justify-between bg-muted/50 rounded-lg p-4">
                  <div>
                    <p className="text-sm font-medium text-card-foreground">{file.name}</p>
                    <p className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                  <button onClick={() => setFile(null)} className="text-destructive hover:text-destructive/80 transition-colors">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              )}
              <Button onClick={handleNext} disabled={!file} className="w-full mt-6 bg-primary text-primary-foreground">
                Process Statement
              </Button>
            </>
          )}

          {step === 3 && (
            <div className="py-8 text-center">
              {error ? (
                <>
                  <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-4" />
                  <h3 className="text-lg font-bold text-card-foreground mb-2">Processing Failed</h3>
                  <p className="text-sm text-destructive mb-4">{error}</p>
                  <Button onClick={resetAndClose} className="bg-primary text-primary-foreground">
                    Try Again
                  </Button>
                </>
              ) : (
              <>
              <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-6" />
              <h3 className="text-lg font-bold text-card-foreground mb-6">Processing your statement...</h3>
              <div className="space-y-3 text-left mb-6">
                {processingSteps.map((label, i) => (
                  <div key={i} className="flex items-center gap-3">
                    {i <= processStep ? (
                      <div className="w-5 h-5 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                        <Check className="h-3 w-3 text-primary-foreground" />
                      </div>
                    ) : (
                      <div className="w-5 h-5 rounded-full border-2 border-border flex-shrink-0" />
                    )}
                    <span className={`text-sm ${i <= processStep ? "text-card-foreground" : "text-muted-foreground"}`}>{label}</span>
                  </div>
                ))}
              </div>
              <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
                <div className="h-full rounded-full bg-primary transition-all duration-150" style={{ width: `${progress}%` }} />
              </div>
              </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
