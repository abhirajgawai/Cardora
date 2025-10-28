'use client';

interface UploadProgressProps {
  fileName: string;
  fileSize: number; // in bytes
  progress: number; // 0-100
  stage: 'uploading' | 'extracting' | 'processing' | 'complete';
  onCancel?: () => void;
}

const stageMessages = {
  uploading: 'Uploading file...',
  extracting: 'Extracting text from PDF...',
  processing: 'AI processing transactions...',
  complete: 'Upload complete!',
};

export default function UploadProgress({
  fileName,
  fileSize,
  progress,
  stage,
  onCancel,
}: UploadProgressProps) {
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="bg-card rounded-2xl border border-border p-8 shadow-sm animate-fade-in">
      {/* File Info Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          {/* PDF Icon */}
          <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
            <svg
              className="w-6 h-6 text-primary"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>

          {/* File Details */}
          <div className="min-w-0 flex-1">
            <p className="font-medium text-foreground truncate" title={fileName}>
              {fileName}
            </p>
            <p className="text-sm text-muted-foreground">{formatFileSize(fileSize)}</p>
          </div>
        </div>

        {/* Cancel Button */}
        {onCancel && stage !== 'complete' && (
          <button
            onClick={onCancel}
            className="text-muted-foreground hover:text-foreground transition-colors p-2 rounded-lg hover:bg-muted"
            title="Cancel upload"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Progress Bar and Status */}
      <div className="space-y-3">
        {/* Status Text */}
        <div className="flex justify-between items-center text-sm">
          <span className="text-muted-foreground flex items-center space-x-2">
            {stage === 'complete' ? (
              <>
                <svg className="w-5 h-5 text-accent" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-accent font-medium">{stageMessages[stage]}</span>
              </>
            ) : (
              <>
                <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                <span>{stageMessages[stage]}</span>
              </>
            )}
          </span>
          <span className="font-semibold text-foreground">{progress}%</span>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Stage Indicators */}
        <div className="flex items-center justify-between pt-2">
          {(['uploading', 'extracting', 'processing', 'complete'] as const).map(
            (stageName, index) => {
              const isActive = stageName === stage;
              const isPast =
                ['uploading', 'extracting', 'processing', 'complete'].indexOf(stage) >
                index;
              const isComplete = stage === 'complete' && stageName === 'complete';

              return (
                <div key={stageName} className="flex items-center">
                  {/* Stage Circle */}
                  <div
                    className={`w-2 h-2 rounded-full transition-all duration-300 ${
                      isComplete
                        ? 'bg-accent'
                        : isPast || isActive
                        ? 'bg-primary'
                        : 'bg-muted'
                    }`}
                  />

                  {/* Connector Line (not for last item) */}
                  {index < 3 && (
                    <div
                      className={`w-8 h-0.5 transition-all duration-300 ${
                        isPast ? 'bg-primary' : 'bg-muted'
                      }`}
                    />
                  )}
                </div>
              );
            }
          )}
        </div>
      </div>
    </div>
  );
}
