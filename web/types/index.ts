export interface GoalArea {
  name: string;
  description: string;
  weekly_hours: number;
  color_emoji: string;
}

export interface Profile {
  user_id: string;
  goal_areas: GoalArea[];
  why_text: string;
  path_a: string;
  path_b: string;
  accomplishments: string[];
  brief_hour: number;
  brief_minute: number;
  timezone: string;
  updated_at?: string;
}

export interface DailyLog {
  id: string;
  user_id: string;
  date: string;
  blocks: Block[];
  completed_block_indices: number[];
  skipped_block_indices: number[];
  framing_type: "fear" | "aspiration" | "accomplishment" | "urgency";
  brief_sent_at?: string;
}

export interface Block {
  index: number;
  goal_area: string;
  color_emoji: string;
  task: string;
  duration_mins: number;
}

export interface Streak {
  user_id: string;
  current_streak: number;
  longest_streak: number;
  last_active_date: string | null;
}
