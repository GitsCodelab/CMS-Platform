import { useState, useCallback } from 'react'
import { oracleAPI } from '../api/client'

export function useOracle() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchRecords = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await oracleAPI.getAll()
      setRecords(Array.isArray(response.data) ? response.data : response.data.data || [])
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch records')
      console.error('Error fetching Oracle records:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  const createRecord = useCallback(async (data) => {
    setLoading(true)
    setError(null)
    try {
      await oracleAPI.create(data)
      await fetchRecords()
      return true
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create record')
      console.error('Error creating Oracle record:', err)
      return false
    } finally {
      setLoading(false)
    }
  }, [fetchRecords])

  const updateRecord = useCallback(async (id, data) => {
    setLoading(true)
    setError(null)
    try {
      await oracleAPI.update(id, data)
      await fetchRecords()
      return true
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update record')
      console.error('Error updating Oracle record:', err)
      return false
    } finally {
      setLoading(false)
    }
  }, [fetchRecords])

  const deleteRecord = useCallback(async (id) => {
    setLoading(true)
    setError(null)
    try {
      await oracleAPI.delete(id)
      await fetchRecords()
      return true
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete record')
      console.error('Error deleting Oracle record:', err)
      return false
    } finally {
      setLoading(false)
    }
  }, [fetchRecords])

  return {
    records,
    loading,
    error,
    fetchRecords,
    createRecord,
    updateRecord,
    deleteRecord,
  }
}
