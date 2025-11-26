export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      equipments: {
        Row: {
          id: number
          name: string
          model: string | null
          location: string | null
          photo_url: string | null
          qr_code_url: string | null
          created_at: string
          updated_at: string | null
        }
        Insert: {
          id?: number
          name: string
          model?: string | null
          location?: string | null
          photo_url?: string | null
          qr_code_url?: string | null
          created_at?: string
          updated_at?: string | null
        }
        Update: {
          id?: number
          name?: string
          model?: string | null
          location?: string | null
          photo_url?: string | null
          qr_code_url?: string | null
          created_at?: string
          updated_at?: string | null
        }
      }
      check_templates: {
        Row: {
          id: number
          equipment_type: string
          item_name: string
          item_type: string
          order_index: number
          created_at: string
        }
        Insert: {
          id?: number
          equipment_type: string
          item_name: string
          item_type: string
          order_index?: number
          created_at?: string
        }
        Update: {
          id?: number
          equipment_type?: string
          item_name?: string
          item_type?: string
          order_index?: number
          created_at?: string
        }
      }
      inspection_records: {
        Row: {
          id: number
          equipment_id: number
          template_item_id: number | null
          status: string | null
          numeric_value: number | null
          photo_url: string | null
          comment: string | null
          reported_by: string | null
          created_at: string
        }
        Insert: {
          id?: number
          equipment_id: number
          template_item_id?: number | null
          status?: string | null
          numeric_value?: number | null
          photo_url?: string | null
          comment?: string | null
          reported_by?: string | null
          created_at?: string
        }
        Update: {
          id?: number
          equipment_id?: number
          template_item_id?: number | null
          status?: string | null
          numeric_value?: number | null
          photo_url?: string | null
          comment?: string | null
          reported_by?: string | null
          created_at?: string
        }
      }
      users: {
        Row: {
          id: number
          email: string | null
          display_name: string | null
          created_at: string
        }
        Insert: {
          id?: number
          email?: string | null
          display_name?: string | null
          created_at?: string
        }
        Update: {
          id?: number
          email?: string | null
          display_name?: string | null
          created_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}
