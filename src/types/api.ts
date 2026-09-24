export interface ErrorDetail {
  field: string;
  message: string;
}

export interface ErrorEnvelope {
  success: false;
  message: string;
  error: {
    code: string;
    details?: ErrorDetail[];
  };
}

export interface ActivityTypeField {
  name: string;
  label: string;
  required: boolean;
  max_length: number;
}

export interface ActivityTypeOption {
  value: string;
  label: string;
  category: string;
  color: string;
  fields: ActivityTypeField[];
}

export type ActivityStatus = "pending" | "published" | "archived";

export interface Activity {
  id: string;
  title: string;
  date: string;
  start_date: string;
  end_date: string;
  type: string;
  activity_type: string;
  description: string | null;
  notes: string | null;
  details: string | null;
  additional_info: string | null;
  category: string;
  campaign_code: string;
  status: ActivityStatus;
  color: string;
  organization: string;
  role: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface CalendarData {
  year: number;
  month?: number | null;
  week_start?: string;
  today: string;
  organization: string;
  role: string;
  activity_types: ActivityTypeOption[];
  activities: Activity[];
}

export interface CalendarResponse {
  success: boolean;
  message: string;
  data: CalendarData;
}

export interface ActivityCreateRequest {
  title: string;
  start_date: string;
  activity_type: string;
  end_date?: string | null;
  details?: string | null;
  additional_info?: string | null;
  category?: string | null;
  status?: string | null;
}

export interface ActivityCreateData extends Activity {
  activity_types: ActivityTypeOption[];
}

export interface ActivityCreateResponse {
  success: boolean;
  message: string;
  data: ActivityCreateData;
}

export interface ActivityUpdateRequest {
  title?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  activity_type?: string | null;
  details?: string | null;
  additional_info?: string | null;
  category?: string | null;
  status?: string | null;
  updated_at?: string | null;
}

export interface ActivityResponse {
  success: boolean;
  message: string;
  data: Activity;
}

export interface ActivityDeleteResponse {
  success: boolean;
  message: string;
  data?: Record<string, never>;
}

export interface LoginRequest {
  email_or_username: string;
  password: string;
}

export interface AuthUser {
  id: string;
  email: string;
  username: string;
  role: string;
}

export interface LoginData {
  access_token: string;
  refresh_token: string;
  token_type?: string;
  user: AuthUser;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  data: LoginData;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ForgotPasswordResponse {
  success: boolean;
  message: string;
  data?: Record<string, never>;
}
