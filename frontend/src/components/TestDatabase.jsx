import React, { useState, useEffect } from 'react'
import '../styles/openui5.css'
import '../styles/custom-spacing.css'
import { useOracle } from '../hooks/useOracle'
import { usePostgres } from '../hooks/usePostgres'

export function TestDatabase() {
  const [activeTab, setActiveTab] = useState('oracle')
  const [showForm, setShowForm] = useState(false)
  const [editingRecord, setEditingRecord] = useState(null)
  const [formData, setFormData] = useState({ name: '', description: '', status: 'active' })
  const [formErrors, setFormErrors] = useState({})
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)

  const oracle = useOracle()
  const postgres = usePostgres()

  const current = activeTab === 'oracle' ? oracle : postgres

  useEffect(() => {
    oracle.fetchRecords()
    postgres.fetchRecords()
  }, [])

  // Reset pagination when tab changes
  useEffect(() => {
    setCurrentPage(1)
  }, [activeTab])

  const normalizeRecords = (records) => {
    return records.map(record => ({
      id: record.ID || record.id,
      name: record.NAME || record.name,
      description: record.DESCRIPTION || record.description,
      status: record.STATUS || record.status,
    }))
  }

  const validateForm = () => {
    const errors = {}
    if (!formData.name.trim()) errors.name = 'Name is required'
    if (!formData.description.trim()) errors.description = 'Description is required'
    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleAddNew = () => {
    setEditingRecord(null)
    setFormData({ name: '', description: '', status: 'active' })
    setFormErrors({})
    setShowForm(true)
  }

  const handleEdit = (record) => {
    setEditingRecord(record)
    setFormData({
      name: record.name || '',
      description: record.description || '',
      status: record.status || 'active',
    })
    setFormErrors({})
    setShowForm(true)
  }

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    if (!validateForm()) return

    let success
    if (editingRecord) {
      success = await current.updateRecord(editingRecord.id, formData)
    } else {
      success = await current.createRecord(formData)
    }

    if (success) {
      setShowForm(false)
      setEditingRecord(null)
      setFormData({ name: '', description: '', status: 'active' })
      setCurrentPage(1)
    }
  }

  const handleDelete = (id) => {
    setConfirmDelete(id)
  }

  const confirmDeleteRecord = async () => {
    if (confirmDelete) {
      await current.deleteRecord(confirmDelete)
      setConfirmDelete(null)
      setCurrentPage(1)
    }
  }

  const records = normalizeRecords(current.records)
  
  // Pagination logic
  const totalPages = Math.ceil(records.length / pageSize)
  const startIndex = (currentPage - 1) * pageSize
  const endIndex = startIndex + pageSize
  const paginatedRecords = records.slice(startIndex, endIndex)

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1)
    }
  }

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1)
    }
  }

  return (
    <div className="ui5-content">
      {/* OpenUI5 Object Page Header */}
      <div className="ui5-object-page-header">
        <h1 className="ui5-object-page-title">📊 Database Management</h1>
        <p className="ui5-object-page-subtitle">View, create, and manage database records across Oracle and PostgreSQL</p>
      </div>

      {/* Alerts */}
      {current.error && (
        <div className="ui5-alert ui5-alert-error" role="alert">
          <span className="ui5-alert-icon">⚠️</span>
          <div>
            <strong>Error</strong>
            <p className="ui5-alert-message">{current.error}</p>
          </div>
        </div>
      )}

      {current.success && (
        <div className="ui5-alert ui5-alert-success" role="alert">
          <span className="ui5-alert-icon">✓</span>
          <span>{current.success}</span>
        </div>
      )}

      {/* OpenUI5 Tab Navigation */}
      <div className="ui5-tabbar">
        <button
          className={`ui5-tab ${activeTab === 'oracle' ? 'active' : ''}`}
          onClick={() => setActiveTab('oracle')}
        >
          <span className="ui5-tab-icon">🔷</span>
          <span className="ui5-tab-label">Oracle Database</span>
          {current.loading && activeTab === 'oracle' && <span className="ui5-spinner">⟳</span>}
        </button>
        <button
          className={`ui5-tab ${activeTab === 'postgres' ? 'active' : ''}`}
          onClick={() => setActiveTab('postgres')}
        >
          <span className="ui5-tab-icon">🐘</span>
          <span className="ui5-tab-label">PostgreSQL</span>
          {current.loading && activeTab === 'postgres' && <span className="ui5-spinner">⟳</span>}
        </button>
      </div>

      {/* Data Table Container */}
      <div className="ui5-table-container">
        {/* Table Toolbar */}
        <div className="ui5-table-toolbar">
          <div className="ui5-toolbar-content">
            <h3 className="ui5-toolbar-title">Records</h3>
            <p className="ui5-toolbar-subtitle">
              Total: {records.length} records | Page {currentPage} of {totalPages || 1} | Showing {paginatedRecords.length} records
            </p>
          </div>
          <button className="ui5-button ui5-button-ghost ui5-button-sm" onClick={handleAddNew}>
            <span>+</span>
            <span>New Record</span>
          </button>
        </div>

        {/* OpenUI5 Table */}
        <div className="ui5-table-wrapper">
          <table className="ui5-table">
            <thead>
              <tr className="ui5-table-header-row">
                <th className="ui5-table-cell">ID</th>
                <th className="ui5-table-cell">Name</th>
                <th className="ui5-table-cell">Description</th>
                <th className="ui5-table-cell">Status</th>
                <th className="ui5-table-cell ui5-table-cell-actions">Actions</th>
              </tr>
            </thead>
            <tbody>
              {paginatedRecords.map((record, idx) => (
                <tr key={record.id} className={`ui5-table-row ${idx % 2 === 0 ? 'even' : 'odd'}`}>
                  <td className="ui5-table-cell">{record.id}</td>
                  <td className="ui5-table-cell">{record.name}</td>
                  <td className="ui5-table-cell ui5-table-cell-description">{record.description}</td>
                  <td className="ui5-table-cell">
                    <span className={`ui5-status-badge ui5-status-${record.status}`}>
                      <span className="ui5-status-dot">●</span>
                      <span>{record.status === 'active' ? 'Active' : 'Inactive'}</span>
                    </span>
                  </td>
                  <td className="ui5-table-cell ui5-table-cell-actions">
                    <button
                      className="ui5-button ui5-button-ghost"
                      onClick={() => handleEdit(record)}
                      title="Edit record"
                    >
                      ✎ Edit
                    </button>
                    <button
                      className="ui5-button ui5-button-danger"
                      onClick={() => handleDelete(record.id)}
                      title="Delete record"
                    >
                      🗑 Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        {records.length > pageSize && (
          <div className="ui5-pagination">
            <button 
              className="ui5-button ui5-button-sm" 
              onClick={handlePreviousPage} 
              disabled={currentPage === 1}
              title="Previous page"
            >
              ← Previous
            </button>
            <span className="ui5-pagination-info">
              Page {currentPage} of {totalPages}
            </span>
            <button 
              className="ui5-button ui5-button-sm" 
              onClick={handleNextPage} 
              disabled={currentPage === totalPages}
              title="Next page"
            >
              Next →
            </button>
          </div>
        )}
      </div>

      {/* OpenUI5 Dialog - Form */}
      {showForm && (
        <div className="ui5-modal-overlay">
          <div className="ui5-modal-dialog">
            <div className="ui5-modal-content">
              <div className="ui5-modal-header">
                <h2 className="ui5-modal-title">
                  {editingRecord ? '✎ Edit Record' : '➕ New Record'}
                </h2>
                <button
                  className="ui5-modal-close"
                  onClick={() => setShowForm(false)}
                  title="Close"
                >
                  ✕
                </button>
              </div>

              <div className="ui5-modal-body">
                <form onSubmit={handleFormSubmit}>
                  {/* Name Field */}
                  <div className="ui5-form-group">
                <label className="ui5-form-label">
                  Record Name <span className="ui5-required">*</span>
                </label>
                <input
                  type="text"
                  className={`ui5-input ${formErrors.name ? 'ui5-input-error' : ''}`}
                  value={formData.name}
                  onChange={(e) => {
                    setFormData({ ...formData, name: e.target.value })
                    if (formErrors.name) setFormErrors({ ...formErrors, name: '' })
                  }}
                  placeholder="Enter record name"
                  maxLength="100"
                />
                {formErrors.name && <span className="ui5-error-message">⚠️ {formErrors.name}</span>}
                <div className="ui5-input-hint">Max 100 characters</div>
              </div>

              {/* Description Field */}
              <div className="ui5-form-group">
                <label className="ui5-form-label">
                  Description <span className="ui5-required">*</span>
                </label>
                <textarea
                  className={`ui5-input ui5-textarea ${formErrors.description ? 'ui5-input-error' : ''}`}
                  value={formData.description}
                  onChange={(e) => {
                    setFormData({ ...formData, description: e.target.value })
                    if (formErrors.description) setFormErrors({ ...formErrors, description: '' })
                  }}
                  placeholder="Enter description"
                  maxLength="500"
                  rows="4"
                />
                {formErrors.description && <span className="ui5-error-message">⚠️ {formErrors.description}</span>}
                <div className="ui5-input-hint">{formData.description.length}/500 characters</div>
                  </div>

                  {/* Status Field */}
                  <div className="ui5-form-group">
                    <label className="ui5-form-label">Status</label>
                    <select
                      className="ui5-input"
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    >
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                </form>
              </div>

              {/* Modal Footer - Buttons */}
              <div className="ui5-modal-footer">
                <button
                  className="ui5-button"
                  type='Reject'
                  onClick={() => setShowForm(false)}
                >
                  Cancel
                </button>
                <button
                  className="ui5-button "
                  type='Emphasized'
                      icon="sap-icon://add"
                  onClick={handleFormSubmit}
                >
                  {editingRecord ? 'Update Record' : 'Create Record'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* OpenUI5 Delete Confirmation Dialog */}
      {confirmDelete && (
        <div className="ui5-modal-overlay">
          <div className="ui5-modal-dialog ui5-modal-sm">
            <div className="ui5-modal-content">
              <div className="ui5-modal-header">
                <h2 className="ui5-modal-title">Confirm Delete</h2>
              </div>
              <div className="ui5-modal-body">
                <p>Are you sure you want to delete this record? This action cannot be undone.</p>
              </div>
              <div className="ui5-modal-footer">
                <button
                  className="ui5-button ui5-button-ghost"
                  onClick={() => setConfirmDelete(null)}
                >
                  Cancel
                </button>
                <button
                  className="ui5-button ui5-button-danger"
                  onClick={confirmDeleteRecord}
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
