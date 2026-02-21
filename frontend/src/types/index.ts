export interface User {
  id: string
  username: string
  full_name: string
  email?: string
  role: 'admin' | 'headmaster' | 'teacher' | 'bursar' | 'clerk'
  is_active: boolean
  last_login?: string
}

export interface Student {
  id: string
  student_id: string
  first_name: string
  last_name: string
  middle_name?: string
  full_name: string
  date_of_birth?: string
  gender: 'male' | 'female' | 'other'
  nationality?: string
  national_id?: string
  religion?: string
  blood_group?: string
  medical_conditions?: string
  allergies?: string
  disability?: string
  doctor_name?: string
  doctor_phone?: string
  guardian_name: string
  guardian_phone: string
  guardian_alt_phone?: string
  guardian_email?: string
  guardian_relationship?: string
  guardian_occupation?: string
  guardian_address?: string
  emergency_contact_name?: string
  emergency_contact_phone?: string
  class_id?: string
  admission_date?: string
  academic_year?: string
  previous_school?: string
  status: 'active' | 'transferred' | 'suspended' | 'graduated' | 'inactive'
  photo_url?: string
  uses_school_transport?: boolean
}

export interface Teacher {
  id: string
  teacher_id: string
  first_name: string
  last_name: string
  full_name: string
  gender?: string
  date_of_birth?: string
  nationality?: string
  national_id?: string
  phone?: string
  alt_phone?: string
  email?: string
  address?: string
  specialization?: string
  qualification?: string
  hire_date?: string
  salary?: number
  bank_name?: string
  bank_account?: string
  tax_id?: string
  status: 'active' | 'on_leave' | 'resigned' | 'terminated'
  photo_url?: string
}

export interface Class {
  id: string
  name: string
  grade_level: string
  stream?: string
  academic_year: string
  capacity: number
  room_number?: string
  class_teacher_id?: string
}

export interface Subject {
  id: string
  name: string
  code: string
  department?: string
  is_elective: boolean
  max_marks: number
  pass_mark: number
  credit_hours: number
}

export interface FeeStructure {
  id: string
  name: string
  fee_type: string
  amount: number
  term: string
  academic_year: string
  is_compulsory: boolean
  class_id?: string
}

export interface FeeInvoice {
  id: string
  invoice_number: string
  student_id: string
  total_amount: number
  paid_amount: number
  discount: number
  balance: number
  status: 'unpaid' | 'partial' | 'paid' | 'overdue' | 'cancelled'
  issue_date: string
  due_date?: string
  term: string
  academic_year: string
  items: FeeInvoiceItem[]
}

export interface FeeInvoiceItem {
  id: string
  description: string
  amount: number
  quantity: number
}

export interface FeePayment {
  id: string
  receipt_number: string
  invoice_id: string
  amount: number
  payment_date: string
  payment_method: string
  reference_number?: string
}

export interface Exam {
  id: string
  name: string
  exam_type: string
  academic_year: string
  term: string
  start_date?: string
  end_date?: string
  is_published: boolean
}

export interface ExamResult {
  id: string
  exam_id: string
  student_id: string
  subject_id: string
  marks_obtained: number
  max_marks: number
  grade?: string
  points?: number
  position?: number
  percentage: number
  is_absent: boolean
  remarks?: string
}

export interface Book {
  id: string
  title: string
  isbn?: string
  author?: string
  publisher?: string
  publication_year?: number
  category?: string
  shelf_location?: string
  total_copies: number
  available_copies: number
}

export interface LibraryIssue {
  id: string
  book_id: string
  student_id?: string
  teacher_id?: string
  issue_date: string
  due_date: string
  return_date?: string
  is_returned: boolean
  days_overdue: number
  fine_amount: number
  calculated_fine: number
  fine_paid: boolean
}

export interface Bus {
  id: string
  registration_number: string
  bus_number: string
  make?: string
  model?: string
  capacity: number
  status: 'active' | 'maintenance' | 'retired'
  driver_name?: string
  driver_phone?: string
}

export interface TransportRoute {
  id: string
  name: string
  bus_id: string
  description?: string
  stops?: string
  morning_departure?: string
  afternoon_departure?: string
  monthly_fee: number
  is_active: boolean
}

export interface InventoryItem {
  id: string
  name: string
  asset_tag?: string
  category: string
  quantity: number
  condition: string
  location?: string
  purchase_date?: string
  purchase_price?: number
  supplier?: string
  serial_number?: string
  is_active: boolean
  notes?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}
