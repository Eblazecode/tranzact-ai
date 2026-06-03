import { useEffect, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { CheckCircle2, FileSpreadsheet, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api, type UploadHistoryItem } from "@/lib/api";
import { useDashboardData } from "@/lib/DashboardContext";

interface PreviousUploadsPageProps {
  onUploadSelected?: () => void | Promise<void>;
}

export function PreviousUploadsPage({ onUploadSelected }: PreviousUploadsPageProps) {
  const { userName } = useDashboardData();
  const navigate = useNavigate();
  const [uploads, setUploads] = useState<UploadHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectingFilename, setSelectingFilename] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    setError(null);

    api.getUploadHistory(userName)
      .then((payload) => {
        if (!cancelled) {
          setUploads(payload.uploads);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Previous uploads could not be loaded.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [userName]);

  const handleSelect = async (upload: UploadHistoryItem) => {
    setSelectingFilename(upload.filename);
    setError(null);

    try {
      await api.selectUpload(userName, upload.filename);
      await onUploadSelected?.();
      void navigate({ to: "/dashboard/$section", params: { section: "overview" } });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "This upload could not be opened.");
      setSelectingFilename(null);
    }
  };

  return (
    <div>
      <p className="text-[13px] text-muted-foreground mb-6">Previous Uploads</p>

      <div className="bg-card border border-border rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-border">
          <h2 className="text-lg font-bold text-card-foreground">Previous Uploads</h2>
        </div>

        {error && (
          <div className="mx-5 mt-5 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-card-foreground">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center gap-3 px-5 py-10 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading previous uploads...
          </div>
        ) : uploads.length === 0 ? (
          <div className="px-5 py-10 text-sm text-muted-foreground">
            No previous uploads found.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="px-5">File Name</TableHead>
                <TableHead>Bank</TableHead>
                <TableHead>Date Uploaded</TableHead>
                <TableHead>Time</TableHead>
                <TableHead className="w-[120px] text-right px-5">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {uploads.map((upload) => {
                const selecting = selectingFilename === upload.filename;

                return (
                  <TableRow key={upload.filename}>
                    <TableCell className="px-5">
                      <div className="flex items-center gap-3">
                        <div className="h-9 w-9 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                          <FileSpreadsheet className="h-4 w-4" />
                        </div>
                        <div className="min-w-0">
                          <p className="font-medium text-card-foreground truncate">{upload.display_name}</p>
                          <p className="text-xs text-muted-foreground truncate">{upload.filename}</p>
                        </div>
                        {upload.is_current && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-green-500/10 px-2 py-1 text-xs font-medium text-green-600">
                            <CheckCircle2 className="h-3 w-3" />
                            Current
                          </span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>{upload.bank_name}</TableCell>
                    <TableCell>{upload.uploaded_date}</TableCell>
                    <TableCell>{upload.uploaded_time}</TableCell>
                    <TableCell className="px-5 text-right">
                      <Button
                        size="sm"
                        variant={upload.is_current ? "secondary" : "default"}
                        onClick={() => void handleSelect(upload)}
                        disabled={selectingFilename !== null}
                      >
                        {selecting ? <Loader2 className="h-4 w-4 animate-spin" /> : "Open"}
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
