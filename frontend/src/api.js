import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const fetchExpenses = () => axios.get(`${API_URL}/expenses`);
export const createExpense = (data) => axios.post(`${API_URL}/expenses`, data);