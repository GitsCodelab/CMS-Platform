import React, { useState } from 'react'
import 'bootstrap/dist/css/bootstrap.min.css'
import { TestDatabase } from './TestDatabase'

export function MainLayout() {
  const [activeMenu, setActiveMenu] = useState('test')
  const [expandedMenu, setExpandedMenu] = useState('test')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const menuItems = [
    {
      id: 'test',
      label: 'Test',
      icon: '🧪',
      submenu: [
        { id: 'test-database', label: 'Database Management' }
      ]
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: '⚙️',
      submenu: []
    },
    {
      id: 'reports',
      label: 'Reports',
      icon: '📊',
      submenu: []
    },
    {
      id: 'help',
      label: 'Help',
      icon: '❓',
      submenu: []
    }
  ]

  const toggleMenu = (menuId) => {
    setExpandedMenu(expandedMenu === menuId ? null : menuId)
  }

  const renderContent = () => {
    switch (activeMenu) {
      case 'test-database':
        return <TestDatabase />
      default:
        return (
          <div className="text-center py-5">
            <p className="text-muted fs-5">Select an item from the menu</p>
          </div>
        )
    }
  }

  return (
    <div className="d-flex" style={{ height: '100vh', backgroundColor: '#f8f9fa' }}>
      {/* Sidebar Menu */}
      <div
        style={{
          width: sidebarOpen ? '256px' : '0px',
          backgroundColor: '#f0f3ff',
          borderRight: '1px solid #dee2e6',
          overflow: 'hidden',
          transition: 'width 300ms ease-in-out',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}
      >
        <div className="p-4 border-bottom">
          <h4 className="mb-0" style={{ backgroundImage: 'linear-gradient(to right, #2563eb, #4f46e5)', backgroundClip: 'text', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            CMS Platform
          </h4>
        </div>

        <nav className="mt-4" style={{ width: '256px' }}>
          {menuItems.map((item) => (
            <div key={item.id}>
              <button
                onClick={() => {
                  if (item.submenu.length > 0) {
                    toggleMenu(item.id)
                  } else {
                    setActiveMenu(item.id)
                  }
                }}
                className="btn btn-link w-100 text-start px-3 py-2 d-flex justify-content-between align-items-center"
                style={{
                  backgroundColor: expandedMenu === item.id ? '#dbeafe' : 'transparent',
                  borderLeft: expandedMenu === item.id ? '4px solid #2563eb' : 'none',
                  color: '#1f2937',
                  textDecoration: 'none',
                  paddingLeft: expandedMenu === item.id ? 'calc(0.75rem - 4px)' : '0.75rem'
                }}
              >
                <div className="d-flex align-items-center gap-3">
                  <span className="fs-5">{item.icon}</span>
                  <span className="fw-500">{item.label}</span>
                </div>
                {item.submenu.length > 0 && (
                  <span
                    style={{
                      transform: expandedMenu === item.id ? 'rotate(180deg)' : 'rotate(0deg)',
                      transition: 'transform 200ms',
                      color: '#4b5563'
                    }}
                  >
                    ▼
                  </span>
                )}
              </button>

              {/* Submenu */}
              {item.submenu.length > 0 && expandedMenu === item.id && (
                <div style={{ backgroundColor: '#dbeafe' }}>
                  {item.submenu.map((subitem) => (
                    <button
                      key={subitem.id}
                      onClick={() => setActiveMenu(subitem.id)}
                      className="btn btn-link w-100 text-start ps-5 py-2"
                      style={{
                        backgroundColor: activeMenu === subitem.id ? '#93c5fd' : 'transparent',
                        color: activeMenu === subitem.id ? '#1e40af' : '#374151',
                        fontWeight: activeMenu === subitem.id ? '600' : 'normal',
                        textDecoration: 'none'
                      }}
                    >
                      {subitem.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="d-flex flex-column flex-grow-1">
        {/* Header */}
        <header className="bg-white border-bottom">
          <div className="px-4 py-4 d-flex align-items-center justify-content-between">
            <div className="d-flex align-items-center gap-3">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="btn btn-light"
                title={sidebarOpen ? 'Hide menu' : 'Show menu'}
                style={{ padding: '0.5rem 0.75rem' }}
              >
                <span style={{ fontSize: '1.5rem' }}>{sidebarOpen ? '☰' : '▶'}</span>
              </button>
              <h3 className="mb-0 text-dark">
                {menuItems
                  .flatMap((item) => [
                    { id: item.id, label: item.label },
                    ...item.submenu
                  ])
                  .find((item) => item.id === activeMenu)?.label || 'Dashboard'}
              </h3>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="flex-grow-1 overflow-auto px-4 py-4">
          {renderContent()}
        </main>
      </div>
    </div>
  )
}
