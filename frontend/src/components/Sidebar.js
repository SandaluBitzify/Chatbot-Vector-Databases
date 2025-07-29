import { motion } from "framer-motion"
import { FiUpload, FiMessageCircle, FiDatabase } from "react-icons/fi"

const Sidebar = ({ activeSection, setActiveSection }) => {
  const menuItems = [
    {
      id: "upload",
      label: "Upload Documents",
      icon: FiUpload,
      description: "Upload and process your files",
    },
    {
      id: "chat",
      label: "Chat Interface",
      icon: FiMessageCircle,
      description: "Ask questions about your documents",
    },
  ]

  return (
    <motion.aside
      className="sidebar"
      initial={{ x: -280 }}
      animate={{ x: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      <div className="sidebar-header">
        <div className="logo">
          <div className="logo-icon">
            <FiDatabase size={24} />
          </div>
          <span>DocuChat AI</span>
        </div>
      </div>

      <nav>
        <ul className="nav-menu">
          {menuItems.map((item) => (
            <li key={item.id} className="nav-item">
              <motion.a
                href="#"
                className={`nav-link ${activeSection === item.id ? "active" : ""}`}
                onClick={(e) => {
                  e.preventDefault()
                  setActiveSection(item.id)
                }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <item.icon size={20} />
                <div>
                  <div>{item.label}</div>
                  <small style={{ opacity: 0.7, fontSize: "0.8rem" }}>{item.description}</small>
                </div>
              </motion.a>
            </li>
          ))}
        </ul>
      </nav>
    </motion.aside>
  )
}

export default Sidebar
