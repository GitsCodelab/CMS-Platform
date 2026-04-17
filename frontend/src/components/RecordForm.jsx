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
    <div className="card">
      <div className="card-header bg-primary text-white">
        <h5 className="mb-0">{initialData ? 'Edit Record' : 'Add New Record'}</h5>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="id" className="form-label">ID</label>
            <input
              type="text"
              className={`form-control ${errors.id ? 'is-invalid' : ''}`}
              id="id"
              name="id"
              value={formData.id}
              onChange={handleChange}
              disabled={!!initialData}
            />
            {errors.id && <div className="invalid-feedback d-block">{errors.id}</div>}
          </div>

          <div className="mb-3">
            <label htmlFor="name" className="form-label">Name</label>
            <input
              type="text"
              className={`form-control ${errors.name ? 'is-invalid' : ''}`}
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
            />
            {errors.name && <div className="invalid-feedback d-block">{errors.name}</div>}
          </div>

          <div className="mb-3">
            <label htmlFor="description" className="form-label">Description</label>
            <textarea
              className="form-control"
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="3"
            />
          </div>

          <div className="mb-3">
            <label htmlFor="status" className="form-label">Status</label>
            <select
              className="form-select"
              id="status"
              name="status"
              value={formData.status}
              onChange={handleChange}
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          <div className="d-grid gap-2">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save'}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
