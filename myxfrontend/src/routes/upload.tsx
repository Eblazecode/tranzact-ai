import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Sparkles, Upload, FileText, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { api, type SupportedBank, type PreprocessingResponse } from "@/lib/api";
import { isAuthenticated, getCurrentUserName } from "@/lib/auth";

export const Route = createFileRoute("/upload")({
  beforeLoad: () => {
    if (!isAuthenticated()) {
      throw redirect({ to: "/login" });
    }
  },
  head: () => ({
    meta: [
      { title: "Upload Statement - TransacAI" },
      { name: "description", content: "Upload your bank statement for AI-powered financial analysis." },
    ],
  }),
  component: UploadPage,
});

const BANKS = [
  { name: "OPay", formats: ["CSV", "Excel"], icon: "📱" },
  { name: "GTBank", formats: ["PDF"], icon: "🏦" },
  { name: "Moniepoint", formats: ["CSV", "Excel"], icon: "💳" },
  { name: "Ecobank", formats: ["CSV", "Excel"], icon: "🌍" },
  { name: "Zenith Bank", formats: ["PDF"], icon: "🏛️" },
];

function UploadPage() {
  const navigate = useNavigate();
  const userName = getCurrentUserName();
  const [selectedBank, setSelectedBank] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<PreprocessingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setError(null);
      setResult(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !selectedBank) {
      setError("Please select a bank and upload a file.");
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const response = await api.uploadBankStatement(file, userName, selectedBank);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const handleGoToDashboard = () => {
    navigate({ to: "/dashboard" });
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-6">
      <div className="w-full max-w-lg">
        <div className="mb-6 text-center">
          <div className="mb-2 flex items-center justify-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">TransacAI</span>
          </div>
          <h1 className="text-2xl font-bold">Upload Bank Statement</h1>
          <p className="text-sm text-muted-foreground">
            Upload your bank statement to get AI-powered financial insights
          </p>
        </div>

        <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
          {result ? (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-green-600">
                <CheckCircle className="h-5 w-5" />
                <span className="font-semibold">Statement Processed Successfully!</span>
              </div>
              <div className="space-y-2 rounded-lg bg-muted/50 p-4 text-sm">
                <p><strong>Bank:</strong> {result.bank_name}</p>
                {result.statement_user_name && <p><strong>Account Name:</strong> {result.statement_user_name}</p>}
                <p><strong>Transactions:</strong> {result.row_count} rows</p>
                <p><strong>Date Range:</strong> {result.date_range}</p>
                <p><strong>Categories:</strong> {result.categories.join(", ")}</p>
              </div>
              <Button onClick={handleGoToDashboard} className="w-full">
                Go to Dashboard
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Bank Selection */}
              <div>
                <Label className="mb-2 block">Select Your Bank</Label>
                <div className="grid grid-cols-2 gap-2">
                  {BANKS.map((bank) => (
                    <button
                      key={bank.name}
                      type="button"
                      onClick={() => { setSelectedBank(bank.name); setError(null); }}
                      className={`flex items-center gap-2 rounded-lg border p-3 text-left text-sm transition-colors ${
                        selectedBank === bank.name
                          ? "border-primary bg-primary/10 text-primary"
                          : "border-border hover:border-primary/50"
                      }`}
                    >
                      <span className="text-lg">{bank.icon}</span>
                      <div>
                        <div className="font-medium">{bank.name}</div>
                        <div className="text-xs text-muted-foreground">{bank.formats.join(", ")}</div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* File Upload */}
              <div>
                <Label htmlFor="file" className="mb-2 block">Bank Statement File</Label>
                <div className="relative">
                  <Input
                    id="file"
                    type="file"
                    accept=".csv,.xlsx,.xls,.pdf"
                    onChange={handleFileChange}
                    className="cursor-pointer"
                  />
                  {file && (
                    <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
                      <FileText className="h-4 w-4" />
                      <span>{file.name} ({(file.size / 1024).toFixed(1)} KB)</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="flex items-center gap-2 rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {/* Submit */}
              <Button
                type="submit"
                disabled={uploading || !file || !selectedBank}
                className="w-full"
              >
                {uploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing Statement...
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload & Process
                  </>
                )}
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
