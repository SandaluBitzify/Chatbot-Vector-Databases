"use client"

import { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { FiSend, FiUser, FiCpu, FiWifi, FiWifiOff, FiLoader } from "react-icons/fi"
import toast from "react-hot-toast"
import { apiService } from "../services/api"

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: "bot",
      content: "Hello! I'm your document assistant. Upload some documents and ask me questions about them!",
      timestamp: new Date(),
    },
  ])
  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState("checking")
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    testBackendConnection()
  }, [])

  const testBackendConnection = async () => {
    try {
      setConnectionStatus("checking")
      const result = await apiService.testConnection()

      if (result.success) {
        setConnectionStatus("connected")
        console.log("Chat: Backend connection successful")
      } else {
        setConnectionStatus("disconnected")
        console.log("Chat: Backend connection failed")
      }
    } catch (error) {
      setConnectionStatus("disconnected")
      console.error("Chat: Backend connection error:", error)
    }
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    if (connectionStatus !== "connected") {
      toast.error("Please wait for backend connection or check if Flask server is running")
      return
    }

    const userMessage = {
      id: Date.now(),
      type: "user",
      content: inputMessage.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputMessage("")
    setIsLoading(true)

    console.log(`Sending message: "${userMessage.content}"`)

    try {
      const response = await apiService.sendMessage(userMessage.content)
      console.log("Chat response received:", response)

      const botMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: response.reply || "Sorry, I couldn't process your request.",
        timestamp: new Date(),
        powered_by: response.powered_by,
      }

      setMessages((prev) => [...prev, botMessage])

      if (response.reply) {
        toast.success("Response received")
      }
    } catch (error) {
      console.error("Chat error:", error)

      let errorMessage = "Sorry, something went wrong. Please try again."

      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.message.includes("Network Error")) {
        errorMessage = "Cannot connect to server. Please check if Flask backend is running on port 5000."
        setConnectionStatus("disconnected")
      } else if (error.code === "ECONNREFUSED") {
        errorMessage = "Connection refused. Please start your Flask server."
        setConnectionStatus("disconnected")
      } else {
        errorMessage = error.message
      }

      const errorBotMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: errorMessage,
        timestamp: new Date(),
        isError: true,
      }

      setMessages((prev) => [...prev, errorBotMessage])
      toast.error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const formatMessage = (content) => {
    return content
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/\n/g, "<br/>")
  }

  const LoadingDots = () => (
    <div className="loading-dots">
      <div className="loading-dot"></div>
      <div className="loading-dot"></div>
      <div className="loading-dot"></div>
    </div>
  )

  const ConnectionStatus = () => (
    <div className={`connection-status ${connectionStatus}`} style={{ margin: "1.5rem" }}>
      {connectionStatus === "connected" && <FiWifi />}
      {connectionStatus === "disconnected" && <FiWifiOff />}
      {connectionStatus === "checking" && <FiLoader className="animate-spin" />}

      <span>
        {connectionStatus === "connected" && "Backend Connected - Ready to chat!"}
        {connectionStatus === "disconnected" && "Backend Disconnected - Please start Flask server on port 5000"}
        {connectionStatus === "checking" && "Checking backend connection..."}
      </span>

      {connectionStatus === "disconnected" && <button onClick={testBackendConnection}>Retry</button>}
    </div>
  )

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <ConnectionStatus />

      <div className="chat-container">
        <div className="chat-messages">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                className={`message message-${message.type}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                <div className="message-content">
                  <div className="message-header">
                    <div className="message-avatar">
                      {message.type === "user" ? <FiUser size={12} /> : <FiCpu size={12} />}
                    </div>
                    <span className="message-author">{message.type === "user" ? "You" : "DocuChat AI"}</span>
                    <span className="message-time">{message.timestamp.toLocaleTimeString()}</span>
                  </div>

                  <div
                    className="message-text"
                    dangerouslySetInnerHTML={{
                      __html: formatMessage(message.content),
                    }}
                    style={{
                      color: message.isError ? "#dc2626" : "#171717",
                    }}
                  />

                  {message.powered_by && (
                    <div className="message-powered-by">Powered by {String(message.powered_by)}</div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              className="message message-bot"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <div className="message-content">
                <div className="message-header">
                  <div className="message-avatar">
                    <FiCpu size={12} />
                  </div>
                  <span className="message-author">DocuChat AI</span>
                </div>
                <LoadingDots />
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <textarea
            ref={inputRef}
            className="chat-input"
            placeholder={
              connectionStatus === "connected" ? "Message DocuChat AI..." : "Please wait for backend connection..."
            }
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading || connectionStatus !== "connected"}
            rows={1}
            style={{
              opacity: connectionStatus !== "connected" ? 0.5 : 1,
            }}
          />

          <motion.button
            className="send-button"
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading || connectionStatus !== "connected"}
            whileHover={{ scale: connectionStatus === "connected" ? 1.02 : 1 }}
            whileTap={{ scale: connectionStatus === "connected" ? 0.98 : 1 }}
          >
            <FiSend size={16} />
          </motion.button>
        </div>
      </div>
    </div>
  )
}

export default Chat
