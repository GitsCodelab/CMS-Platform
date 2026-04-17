import React, { useState, useEffect } from 'react'
import { DataTable } from './DataTable'
import { RecordForm } from './RecordForm'
import { useOracle } from '../hooks/useOracle'
import { usePostgres } from '../hooks/usePostgres'

export function TestDatabase() {
  const [activeTab, setActiveTab] = useState('oracle')
  const [showForm, setShowForm] = useState(false)
  const [editingRecord, setEditingRecord] = useState(null)
  const [confirmDelete, setConfirmDelete] = useState(null)

  const oracle = useOracle()
  const postgres = usePostgres()

  const current = activeTab === 'oracle' ? oracle : postgres

  useEffect(() => {
    oracle.fetchRecords()
    postgres.fetchRecords()
  }, [])

  const handleAddNew = () => {
    setEditingRecord(null)
    setShowForm(true)
  }

  const handleEdit = (record) => {
    setEditingRecord(record)
    setShowForm(true)
  }

  const handleFormSubmit = async (formData) => {
    let success
    if (editingRecord) {
      success = await current.updateRecord(editingRecord.id, formData)
    } else {
      success = await current.createRecord(formData)
    }
    if (success) {
      setShowForm(false)
      setEditingRecord(null)
    }
  }

  const handleDelete = (id) => {
    setConfirmDelete(id)
  }

  const confirmDeleteRecord = async () => {
    if (confirmDelete) {
      await current.deleteRecord(confirmDelete)
      setConfirmDelete(null)
    }
  }

  const columns = ['id', 'name', 'description', 'status']

  // Normalize record data (API returns uppercase)
  const normalizeRecords = (records) => {
    return records.map(record => ({
      id: record.ID || record.id,
      name: record.NAME || record.name,
      description: record.DESCRIPTION || record.description,
      status: record.STATUS || record.status,
    }))
  }

  return (
    <div>
      {/* Error Alert */}
      {current.error && (
        <div className="alert alert-danger mb-4" role="alert">
          {current.error}
        </div>
      )}

      {/* Tabs */}
      <div className="mb-4">
        <ul className="nav nav-tabs">
          <li className="nav-item">
            <button
              onClick={() => setActiveTab('oracle')}
              className={`nav-link ${activeTab === 'oracle' ? 'active' : ''}`}
            >
              Oracle Database
            </button>
          </li>
          <li className="nav-item">
            <button
              onClick={() => setActiveTab('postgres')}
              className={`nav-link ${activeTab === 'postgres' ? 'active' : ''}`}
            >
              PostgreSQL Database
            </button>
          </li>
        </ul>
      </div>

      {/* Content */}
      <div className="row">
        {/* Form Section */}
        {showForm && (
          <div className="col-lg-3">
            <RecordForm
              onSubmit={handleFormSubmit}
              initialData={editingRecord}
              onCancel={() => {
                setShowForm(false)
                setEditingRecord(null)
              }}
              loading={current.loading}
            />
          </div>
        )}

        {/* Table Section */}
        <div className={showForm ? 'col-lg-9' : 'col-lg-12'}>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h4 className="mb-0">
              {activeTab === 'oracle' ? 'Oracle' : 'PostgreSQL'} Records
            </h4>
            {!showForm && (
              <button
                onClick={handleAddNew}
                className="btn btn-success"
              >
                + Add New
              </button>
            )}
          </div>

          <DataTable
            columns={columns}
            data={normalizeRecords(current.records)}
            onEdit={handleEdit}
            onDelete={handleDelete}
            loading={current.loading}
          />
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {confirmDelete && (
        <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-sm">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Confirm Delete</h5>
                <button type="button" className="btn-close" onClick={() => setConfirmDelete(null)}></button>
              </div>
              <div className="modal-body">
                <p>Are you sure you want to delete this record?</p>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setConfirmDelete(null)}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn btn-danger"
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
