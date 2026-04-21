import React, { useState, useEffect } from 'react'

export function RecordForm({ onSubmit, initialData, onCancel, loading }) {
  const [formData, setFormData] = useState({
    id: '',
    name: '',
    description: '',
    status: 'active'
  })

  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (initialData) {
      setFormData(initialData)
    } else {
      setFormData({
        id: '',
        name: '',
        description: '',
        status: 'active'
      })
    }
    setErrors({})
  }, [initialData])

  const validateForm = () => {
    const newErrors = {}
    if (!formData.id && !initialData) {
      newErrors.id = 'ID is required'
    }
    if (!formData.name) {
      newErrors.name = 'Name is required'
    }
    return newErrors
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const newErrors = validateForm()
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }
    onSubmit(formData)
  }

  return (
    <div style={{
      backgroundColor: '#FFFFFF',
      borderRadius: '4px',
      border: '1px solid var(--sap-border-light)',
      boxShadow: 'var(--sap-shadow)',
      overflow: 'hidden'
    }}>
      {/* Form Header */}
      <div style={{
        backgroundColor: '#F0F0F0',
        borderBottom: '1px solid var(--sap-border-light)',
        padding: '1.5rem',
        borderLeft: '4px solid var(--sap-primary)'
      }}>
        <h5 style={{
          margin: 0,
          fontSize: '1.125rem',
          fontWeight: '600',
          color: 'var(--sap-primary)'
        }}>
          {initialData ? '✏️ Edit Record' : '➕ Add New Record'}
        </h5>
      </div>

      {/* Form Body */}
      <div style={{ padding: '2rem' }}>
        <form onSubmit={handleSubmit}>
          {/* ID Field */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label htmlFor="id" style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: 'var(--sap-text)'
            }}>
              ID
            </label>
            <input
              type="text"
              className="form-control"
              id="id"
              name="id"
              value={formData.id}
              onChange={handleChange}
              disabled={!!initialData}
              style={{
                borderColor: errors.id ? 'var(--sap-error)' : 'var(--sap-border)',
                backgroundColor: initialData ? '#F5F5F5' : 'white'
              }}
            />
            {errors.id && <div style={{
              color: 'var(--sap-error)',
              fontSize: '0.8125rem',
              marginTop: '0.375rem'
            }}>⚠️ {errors.id}</div>}
          </div>

          {/* Name Field */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label htmlFor="name" style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: 'var(--sap-text)'
            }}>
              Name
            </label>
            <input
              type="text"
              className="form-control"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              style={{
                borderColor: errors.name ? 'var(--sap-error)' : 'var(--sap-border)'
              }}
            />
            {errors.name && <div style={{
              color: 'var(--sap-error)',
              fontSize: '0.8125rem',
              marginTop: '0.375rem'
            }}>⚠️ {errors.name}</div>}
          </div>

          {/* Description Field */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label htmlFor="description" style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: 'var(--sap-text)'
            }}>
              Description
            </label>
            <textarea
              className="form-control"
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="3"
              style={{
                borderColor: 'var(--sap-border)',
                resize: 'vertical'
              }}
            />
          </div>

          {/* Status Field */}
          <div style={{ marginBottom: '2rem' }}>
            <label htmlFor="status" style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: 'var(--sap-text)'
            }}>
              Status
            </label>
            <select
              className="form-select"
              id="status"
              name="status"
              value={formData.status}
              onChange={handleChange}
              style={{
                borderColor: 'var(--sap-border)'
              }}
            >
              <option value="active">✓ Active</option>
              <option value="inactive">✗ Inactive</option>
            </select>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button
              type="submit"
              disabled={loading}
              style={{
                flex: 1,
                padding: '0.75rem 1.5rem',
                backgroundColor: loading ? '#CCC' : 'var(--sap-primary)',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '0.875rem',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                if (!loading) {
                  e.target.style.backgroundColor = 'var(--sap-primary-dark)'
                  e.target.style.transform = 'translateY(-1px)'
                  e.target.style.boxShadow = 'var(--sap-shadow-md)'
                }
              }}
              onMouseLeave={(e) => {
                if (!loading) {
                  e.target.style.backgroundColor = 'var(--sap-primary)'
                  e.target.style.transform = 'translateY(0)'
                  e.target.style.boxShadow = 'var(--sap-shadow)'
                }
              }}
            >
              💾 {loading ? 'Saving...' : 'Save Record'}
            </button>
            <button
              type="button"
              onClick={onCancel}
              disabled={loading}
              style={{
                flex: 1,
                padding: '0.75rem 1.5rem',
                backgroundColor: '#FFFFFF',
                color: 'var(--sap-secondary)',
                border: '1px solid var(--sap-border)',
                borderRadius: '4px',
                fontSize: '0.875rem',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                if (!loading) {
                  e.target.style.backgroundColor = 'var(--sap-secondary-light)'
                  e.target.style.transform = 'translateY(-1px)'
                }
              }}
              onMouseLeave={(e) => {
                if (!loading) {
                  e.target.style.backgroundColor = '#FFFFFF'
                  e.target.style.transform = 'translateY(0)'
                }
              }}
            >
              ✕ Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
