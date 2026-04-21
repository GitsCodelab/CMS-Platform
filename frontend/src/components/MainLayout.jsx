import React, { useState } from 'react'
import '../styles/openui5.css'
import '../styles/custom-spacing.css'
import { TestDatabase } from './TestDatabase'

export function MainLayout() {
  const [activeMenu, setActiveMenu] = useState('test-database')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const menuItems = [
    {
      id: 'test',
      label: 'Data Management',
      icon: '📊',
      submenu: [
        { id: 'test-database', label: 'Database Management' }
      ]
    },
    {
      id: 'payment',
      label: 'Payment Processing',
      icon: '💳',
      submenu: [
        { id: 'payment-jpos', label: 'jPOS Transactions' },
        { id: 'payment-reports', label: 'Payment Reports' }
      ]
    },
    {
      id: 'workflows',
      label: 'Workflows',
      icon: '🔄',
      submenu: [
        { id: 'workflow-list', label: 'Active Workflows' },
        { id: 'workflow-schedule', label: 'Scheduling' }
      ]
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: '⚙️',
      submenu: [
        { id: 'settings-config', label: 'Configuration' },
        { id: 'settings-users', label: 'User Management' }
      ]
    },
    {
      id: 'help',
      label: 'Help & Support',
      icon: '❓',
      submenu: []
    }
  ]

  const renderContent = () => {
    if (activeMenu === 'test-database') {
      return <TestDatabase />
    }
    return (
      <div className="ui5-empty-state">
        <p>Select an item from the menu</p>
      </div>
    )
  }

  return (
    <div className="ui5-shell">
      {/* SAP Fiori Shell Header */}
      <header className="ui5-shell-header">
        <button 
          className="ui5-shell-header-button"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          title="Toggle sidebar"
        >
          ☰
        </button>
        <h1 className="ui5-shell-title">🚀 CMS Platform</h1>
        <div className="ui5-shell-header-spacer"></div>
        <span className="ui5-shell-user">👤 Administrator</span>
      </header>

      <div className="ui5-shell-body">
        {/* OpenUI5 Side Navigation */}
        <aside className={`ui5-sidenav ${sidebarOpen ? 'open' : 'closed'}`}>
          <nav className="ui5-sidenav-content">
            {menuItems.map(menu => (
              <div key={menu.id} className="ui5-sidenav-group">
                <a 
                  href="#"
                  className="ui5-sidenav-item"
                  onClick={(e) => {
                    e.preventDefault()
                    if (menu.submenu.length > 0) {
                      setActiveMenu(menu.submenu[0].id)
                    }
                  }}
                >
                  <span className="ui5-sidenav-icon">{menu.icon}</span>
                  <span className="ui5-sidenav-label">{menu.label}</span>
                </a>
                {menu.submenu.length > 0 && (
                  <div className="ui5-sidenav-submenu">
                    {menu.submenu.map(item => (
                      <a
                        key={item.id}
                        href="#"
                        className={`ui5-sidenav-subitem ${activeMenu === item.id ? 'active' : ''}`}
                        onClick={(e) => {
                          e.preventDefault()
                          setActiveMenu(item.id)
                        }}
                      >
                        {item.label}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </nav>
          
          {/* Sidebar Footer */}
          <div className="ui5-sidenav-footer">
            <div className="ui5-sidenav-version">v1.0.0 • OpenUI5</div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="ui5-main-content">
          <div className="ui5-page">
            {renderContent()}
          </div>
        </main>
      </div>

      {/* Page Footer */}
      <footer className="ui5-shell-footer">
        <p>© 2026 CMS Platform. All rights reserved. | Built with React + OpenUI5 + FastAPI</p>
      </footer>
    </div>
  )
}
