/**
 * Category domain model
 */

export interface Category {
  id: string;
  name: string;
  icon: string;
  color: string;
  is_custom: boolean;
  created_at: string;
}
