export interface ApiErrorDetail {
  field: string;
  message: string;
}

export interface ApiErrorBody {
  code: string;
  details?: ApiErrorDetail[] | Record<string, unknown> | null;
}

export interface ApiErrorResponse {
  success: false;
  message: string;
  error: ApiErrorBody;
}

export interface ApiSuccessResponse<T> {
  success: true;
  message: string;
  data: T;
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
  token_type: 'bearer';
  user: AuthUser;
}

export type LoginResponse = ApiSuccessResponse<LoginData>;

export interface ForgotPasswordRequest {
  email: string;
}

export type ForgotPasswordResponse = ApiSuccessResponse<Record<string, never>>;

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

export type ActivityStatus = 'pending' | 'published' | 'archived';

export interface ActivityOut {
  id: string;
  title: string;
  date: string;
  start_date: string;
  end_date: string;
  type: string;
  activity_type: string;
  description?: string | null;
  notes?: string | null;
  details?: string | null;
  additional_info?: string | null;
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

export interface ActivityCreateData extends ActivityOut {
  activity_types: ActivityTypeOption[];
}

export interface CalendarData {
  year: number;
  month?: number | null;
  week_start: 'monday';
  today: string;
  organization: string;
  role: string;
  activity_types: ActivityTypeOption[];
  activities: ActivityOut[];
}

export type CalendarResponse = ApiSuccessResponse<CalendarData>;

export interface ActivityCreateRequest {
  title: string;
  start_date: string;
  end_date?: string | null;
  activity_type: string;
  details?: string | null;
  additional_info?: string | null;
  category?: string | null;
  status?: ActivityStatus | null;
}

export type ActivityCreateResponse = ApiSuccessResponse<ActivityCreateData>;

export type ActivityGetResponse = ApiSuccessResponse<ActivityOut>;

export interface ActivityUpdateRequest {
  title?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  activity_type?: string | null;
  details?: string | null;
  additional_info?: string | null;
  category?: string | null;
  status?: ActivityStatus | null;
  updated_at?: string | null;
}

export type ActivityUpdateResponse = ApiSuccessResponse<ActivityOut>;

export type ActivityDeleteResponse = ApiSuccessResponse<Record<string, never>>;

export interface CalendarQueryParams {
  year?: number;
  month?: number;
  category?: string[];
  activity_type?: string[];
}

export interface HealthData {
  status?: string;
  [key: string]: unknown;
}

export type HealthResponse = ApiSuccessResponse<HealthData>;
