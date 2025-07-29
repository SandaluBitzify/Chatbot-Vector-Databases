import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Toaster } from "react-hot-toast"
import Sidebar from "./components/Sidebar"
import Upload from "./components/Upload"
import Chat from "./components/Chat"
import "./App.css"

function App() {
  const [activeSection, setActiveSection] = useState("upload")

  const renderContent = () => {
    switch (activeSection) {
      case "upload":
        return <Upload />
      case "chat":
        return <Chat />
      default:
        return <Upload />
    }
  }

  return (
    <div className="app">
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: "rgba(255, 255, 255, 0.1)",
            backdropFilter: "blur(20px)",
            color: "white",
            border: "1px solid rgba(255, 255, 255, 0.2)",
            borderRadius: "12px",
          },
        }}
      />

      <Sidebar activeSection={activeSection} setActiveSection={setActiveSection} />

      <main className="main-content">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeSection}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {renderContent()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App
