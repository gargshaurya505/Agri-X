import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  UploadCloud, 
  Image as ImageIcon, 
  X, 
  AlertCircle, 
  ScanSearch, 
  CheckCircle2, 
  RefreshCw,
  FileText
} from 'lucide-react';
import { predictImage } from '../services/predictionService';
import { savePredictionToHistory } from '../services/historyService';

const MAX_FILE_SIZE = 10 * 1024 * 1024;
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];

export const DetectPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const validateAndSetFile = (file) => {
    setErrorMessage(null);

    if (!file) return;

    if (!ALLOWED_TYPES.includes(file.type.toLowerCase())) {
      setErrorMessage('Unsupported format. Please upload JPG, PNG, or WEBP images.');
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setErrorMessage('File exceeds 10 MB limit. Please select a smaller leaf photograph.');
      return;
    }

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    const objectUrl = URL.createObjectURL(file);
    setSelectedFile(file);
    setPreviewUrl(objectUrl);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleClear = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    setErrorMessage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const response = await predictImage(selectedFile);

      const historyItem = {
        prediction_id: response.prediction_id || `pred_${Date.now()}`,
        predicted_class: response.predicted_class,
        display_name: response.display_name,
        confidence: response.confidence,
        top_predictions: response.top_predictions,
        timestamp: new Date().toISOString(),
        model_name: response.model_name || 'ResNet18'
      };
      savePredictionToHistory(historyItem);

      navigate('/results', {
        state: {
          prediction: response,
          previewUrl: previewUrl,
          file: selectedFile
        }
      });
    } catch (err) {
      setErrorMessage(
        err.message || 'Local AI service is not running. Please start the AGRI-X Python service on localhost:8000.'
      );
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">
          Tomato Leaf Disease Diagnostic Scanner
        </h1>
        <p className="text-slate-600 text-sm max-w-xl mx-auto">
          Upload a high-resolution photograph of an individual tomato leaf for local neural network inference and explainability.
        </p>
      </div>

      
      <div className="bg-white rounded-3xl border border-sand-200 p-6 sm:p-10 shadow-sm space-y-6">
        {!previewUrl ? (
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-10 sm:p-16 text-center cursor-pointer transition-all ${
              dragActive
                ? 'border-forest-600 bg-forest-50/50 scale-[0.99]'
                : 'border-sand-300 hover:border-forest-400 hover:bg-sand-50/50'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".jpg,.jpeg,.png,.webp"
              onChange={handleChange}
              className="hidden"
            />
            <div className="space-y-4 max-w-sm mx-auto">
              <div className="w-16 h-16 rounded-2xl bg-forest-50 text-forest-700 flex items-center justify-center mx-auto border border-forest-100 shadow-sm">
                <UploadCloud className="w-8 h-8" />
              </div>
              <div className="space-y-1">
                <p className="text-base font-semibold text-slate-900">
                  Click to browse or drop photograph here
                </p>
                <p className="text-xs text-slate-500">
                  Supports JPG, PNG, or WEBP (Max size: 10 MB)
                </p>
              </div>
              <div className="pt-2">
                <span className="inline-block px-3 py-1 bg-sand-100 text-slate-600 text-xs font-medium rounded-full">
                  100% Private Local Inference
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="relative rounded-2xl overflow-hidden border border-sand-300 max-w-md mx-auto bg-slate-900 shadow-md">
              <img
                src={previewUrl}
                alt="Selected Tomato Leaf"
                className="w-full h-80 object-contain mx-auto"
              />
              <button
                onClick={handleClear}
                disabled={isSubmitting}
                className="absolute top-3 right-3 p-1.5 rounded-full bg-slate-900/80 text-white hover:bg-slate-900 transition-colors"
                title="Remove image"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex items-center justify-between max-w-md mx-auto px-2 text-xs text-slate-500">
              <div className="flex items-center space-x-1.5 truncate">
                <FileText className="w-4 h-4 text-forest-600 flex-shrink-0" />
                <span className="truncate">{selectedFile.name}</span>
              </div>
              <span className="font-mono">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto pt-2">
              <button
                onClick={handleAnalyze}
                disabled={isSubmitting}
                className={`flex-1 inline-flex items-center justify-center space-x-2 py-3 px-6 rounded-xl font-semibold text-white shadow-md transition-all ${
                  isSubmitting
                    ? 'bg-forest-800 cursor-not-allowed opacity-90'
                    : 'bg-forest-700 hover:bg-forest-800'
                }`}
              >
                {isSubmitting ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    <span>Executing Neural Inference...</span>
                  </>
                ) : (
                  <>
                    <ScanSearch className="w-5 h-5" />
                    <span>Analyze Image</span>
                  </>
                )}
              </button>

              <button
                onClick={handleClear}
                disabled={isSubmitting}
                className="px-4 py-3 border border-sand-300 rounded-xl font-semibold text-slate-700 hover:bg-sand-100 transition-colors text-sm"
              >
                Choose Different
              </button>
            </div>
          </div>
        )}

        
        {errorMessage && (
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 flex items-start space-x-3 text-sm">
            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="space-y-1 flex-1">
              <p className="font-semibold text-amber-800">Connection or Validation Notice</p>
              <p className="text-xs text-amber-700 leading-relaxed">{errorMessage}</p>
            </div>
          </div>
        )}
      </div>

      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-600">
        <div className="p-4 rounded-xl bg-white border border-sand-200 space-y-1.5">
          <span className="font-bold text-slate-800">1. Good Lighting</span>
          <p>Photograph in diffuse natural daylight to avoid specular sunlight glare and heavy shadows.</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-sand-200 space-y-1.5">
          <span className="font-bold text-slate-800">2. Individual Leaf Focus</span>
          <p>Frame a single diseased leaflet filling most of the viewport for optimal spatial feature extraction.</p>
        </div>
        <div className="p-4 rounded-xl bg-white border border-sand-200 space-y-1.5">
          <span className="font-bold text-slate-800">3. Lesion Visibility</span>
          <p>Ensure visible necrotic spots, fungal mycelia, or viral curling are sharply in focus.</p>
        </div>
      </div>
    </div>
  );
};
