import { useState, useRef, useEffect } from "react"
import { motion } from "framer-motion"
import { FiUpload, FiFile, FiCheck, FiLoader, FiAlertCircle, FiWifi, FiWifiOff } from "react-icons/fi"
import toast from "react-hot-toast"
import { apiService } from "../services/api"

const Upload = () => {
  const [isDragging, setIsDragging] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [connectionStatus, setConnectionStatus] = useState("checking")
  const fileInputRef = useRef(null)

  const allowedTypes = [".pdf", ".xlsx", ".xls", ".docx", ".txt", ".csv"]

  useEffect(() => {
    testBackendConnection()
    loadExistingFiles()
  }, [])

  const testBackendConnection = async () => {
    try {
      setConnectionStatus("checking")
      const result = await apiService.testConnection()

      if (result.success) {
        setConnectionStatus("connected")
        toast.success("Connected to backend successfully")
      } else {
        setConnectionStatus("disconnected")
        toast.error("Cannot connect to backend. Make sure Flask server is running on port 5000.")
      }
    } catch (error) {
      setConnectionStatus("disconnected")
      toast.error("Backend connection failed. Please check if your Flask server is running.")
    }
  }

  const loadExistingFiles = async () => {
    try {
      const response = await apiService.getFiles()
      if (response.files) {
        const filesArray = Object.entries(response.files).map(([filename, metadata]) => ({
          id: Date.now() + Math.random(),
          name: filename,
          uploadedAt: new Date().toLocaleString(),
          ...metadata,
        }))
        setUploadedFiles(filesArray)
        console.log(`Loaded ${filesArray.length} existing files`)
      }
    } catch (error) {
      console.error("Error loading existing files:", error)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files)
    handleFiles(files)
  }

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files)
    handleFiles(files)
  }

  const handleFiles = (files) => {
    if (connectionStatus !== "connected") {
      toast.error("Please wait for backend connection or check if Flask server is running")
      return
    }

    files.forEach((file) => {
      const fileExt = "." + file.name.split(".").pop().toLowerCase()
      if (allowedTypes.includes(fileExt)) {
        uploadFile(file)
      } else {
        toast.error(`File type ${fileExt} is not supported. Allowed: ${allowedTypes.join(", ")}`)
      }
    })
  }

  const uploadFile = async (file) => {
    console.log(`Starting upload for: ${file.name}`)
    setIsUploading(true)
    setUploadProgress(0)

    const uploadToast = toast.loading(`Uploading ${file.name}...`)

    try {
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev < 90) return prev + 10
          return prev
        })
      }, 200)

      const response = await apiService.uploadFile(file)

      clearInterval(progressInterval)
      setUploadProgress(100)

      if (response) {
        const fileInfo = {
          id: Date.now() + Math.random(),
          name: file.name,
          size: file.size,
          type: file.type,
          uploadedAt: new Date().toLocaleString(),
          ...response,
        }

        setUploadedFiles((prev) => [fileInfo, ...prev])
        toast.dismiss(uploadToast)
        toast.success(`${file.name} uploaded successfully! Found ${response.total_records || 0} records.`)
      }
    } catch (error) {
      console.error("Upload error:", error)
      toast.dismiss(uploadToast)

      let errorMessage = `Failed to upload ${file.name}`
      if (error.response?.data?.error) {
        errorMessage += `: ${error.response.data.error}`
      } else if (error.message.includes("Network Error")) {
        errorMessage += ": Cannot connect to server. Please check if Flask backend is running on port 5000."
      } else if (error.code === "ECONNREFUSED") {
        errorMessage += ": Connection refused. Please start your Flask server."
      } else {
        errorMessage += `: ${error.message}`
      }

      toast.error(errorMessage)

      if (error.message.includes("Network Error") || error.code === "ECONNREFUSED") {
        setConnectionStatus("disconnected")
      }
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const renderSheetInfo = (sheets) => {
    if (!sheets || !Array.isArray(sheets)) return null

    return sheets.map((sheet, index) => {
      if (typeof sheet === "object" && sheet !== null) {
        return (
          <div key={index}>
            • {sheet.name || `Sheet ${index + 1}`}: {sheet.records || 0} records
          </div>
        )
      }
      return <div key={index}>• {String(sheet)}</div>
    })
  }

  const ConnectionStatus = () => (
    <div className={`connection-status ${connectionStatus}`}>
      {connectionStatus === "connected" && <FiWifi />}
      {connectionStatus === "disconnected" && <FiWifiOff />}
      {connectionStatus === "checking" && <FiLoader className="animate-spin" />}

      <span>
        {connectionStatus === "connected" && "Backend Connected"}
        {connectionStatus === "disconnected" && "Backend Disconnected - Please start Flask server on port 5000"}
        {connectionStatus === "checking" && "Checking backend connection..."}
      </span>

      {connectionStatus === "disconnected" && <button onClick={testBackendConnection}>Retry</button>}
    </div>
  )

  return (
    <div style={{ padding: "1.5rem" }}>
      <ConnectionStatus />

      <motion.div
        className="glow-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div
          className={`upload-area ${isDragging ? "dragover" : ""}`}
          onDragOver={connectionStatus === "connected" ? handleDragOver : undefined}
          onDragLeave={connectionStatus === "connected" ? handleDragLeave : undefined}
          onDrop={connectionStatus === "connected" ? handleDrop : undefined}
          onClick={connectionStatus === "connected" ? () => fileInputRef.current?.click() : undefined}
          style={{
            opacity: connectionStatus !== "connected" ? 0.5 : 1,
            cursor: connectionStatus !== "connected" ? "not-allowed" : "pointer",
          }}
        >
          {connectionStatus === "connected" ? (
            <FiUpload className="upload-icon" />
          ) : connectionStatus === "disconnected" ? (
            <FiAlertCircle className="upload-icon" />
          ) : (
            <FiLoader className="upload-icon animate-spin" />
          )}

          <h3 className="upload-text">
            {connectionStatus === "connected"
              ? isDragging
                ? "Drop files here"
                : "Click to upload or drag and drop"
              : connectionStatus === "disconnected"
                ? "Backend disconnected"
                : "Connecting to backend..."}
          </h3>
          <p className="upload-subtext">
            {connectionStatus === "connected"
              ? `Supports: ${allowedTypes.join(", ")}`
              : connectionStatus === "disconnected"
                ? "Please start your Flask server on port 5000"
                : "Please wait..."}
          </p>

          <input
            ref={fileInputRef}
            type="file"
            className="file-input"
            multiple
            accept={allowedTypes.join(",")}
            onChange={handleFileSelect}
            disabled={connectionStatus !== "connected"}
          />
        </div>

        {isUploading && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            style={{ marginTop: "1rem" }}
          >
            <div className="progress-bar">
              <motion.div
                className="progress-fill"
                initial={{ width: 0 }}
                animate={{ width: `${uploadProgress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "0.5rem",
                marginTop: "0.5rem",
              }}
            >
              <FiLoader className="animate-spin" />
              <span style={{ fontSize: "0.875rem", color: "#737373" }}>Processing file... {uploadProgress}%</span>
            </div>
          </motion.div>
        )}
      </motion.div>

      {uploadedFiles.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          style={{ marginTop: "2rem" }}
        >
          <h2 style={{ fontSize: "1.25rem", fontWeight: "600", color: "#171717", marginBottom: "1rem" }}>
            Uploaded Files ({uploadedFiles.length})
          </h2>

          <div className="file-list">
            {uploadedFiles.map((file, index) => (
              <motion.div
                key={file.id}
                className="file-item"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                <div className="file-item-header">
                  <div className="file-item-info">
                    <FiFile className="file-item-icon" size={20} />
                    <div className="file-item-details">
                      <h4>{file.name}</h4>
                      <p>
                        {file.size ? formatFileSize(file.size) : "Unknown size"} • {file.uploadedAt}
                      </p>
                    </div>
                  </div>

                  <div className="file-item-status">
                    {file.total_records !== undefined && <span>{file.total_records} records</span>}
                    <FiCheck size={16} style={{ color: "#16a34a" }} />
                  </div>
                </div>

                {(file.debug_info || file.total_records !== undefined || file.sheets || file.columns) && (
                  <div className="file-item-meta">
                    <strong>Processing Details:</strong>
                    <br />
                    File Type: {file.file_type || "Unknown"}
                    <br />
                    Total Records: {file.total_records || 0}
                    <br />
                    {file.sheets && Array.isArray(file.sheets) && file.sheets.length > 0 && (
                      <>
                        Sheets ({file.sheets.length}):
                        <br />
                        {renderSheetInfo(file.sheets)}
                      </>
                    )}
                    {file.columns && Array.isArray(file.columns) && file.columns.length > 0 && (
                      <>
                        Columns ({file.columns.length}): {file.columns.slice(0, 5).join(", ")}
                        {file.columns.length > 5 && ` ... and ${file.columns.length - 5} more`}
                        <br />
                      </>
                    )}
                    {file.extraction_methods && Array.isArray(file.extraction_methods) && (
                      <>
                        Extraction Methods: {file.extraction_methods.join(", ")}
                        <br />
                      </>
                    )}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}

export default Upload
