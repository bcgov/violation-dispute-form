//This file holds the interfaces for admin.
export interface SearchParameters {
  filterParameters: FilterParameters;
  sortParameters: SortParameters;
}

export enum AdminPageMode {
  NewResponse,
  Archive,
}

export interface FilterParameters {
  search: string;
  createdDate: string;
  archivedDate: string;
  region: number;
  offset: number;
  page: number; //Unused in Django, we use offset records, not offset page
  limit: number;
  isArchived: boolean;
}

export interface SortParameters extends Array<SortParameter> {}

export interface SortParameter {
  prop: string;
  dir: string;
}

export interface SearchResponse {
  count: number;
  next: string;
  previous: string;
  results: Array<TicketResponseContent>;
}

export interface TicketResponseContent {
  created_date: Date | string;
  updated_date: Date | string;
  emailed_date: Date | string;

  first_name: string;
  middle_name: string;
  last_name: string;

  email: string;

  hearing_attendance: string;
  hearing_location: Location;

  ticket_number: string;
  ticket_date: Date;
  deadline_date: Date | string;
  dispute_type: string;
  pdf_filename: string;
  archived_by: User;
  archived_date: Date | string;
  printed_by: User;
  printed_date: Date;
}

export interface User {
  first_name: string;
  last_name: string;
}

export interface Location {
  id: number;
  name: string;
  region: Region;
}

export interface Region {
  id: number;
  name: string;
}

export interface ByRegionCount {
  name: string;
  id_: number;
  count: number;
}

export interface TotalCount {
  count: number;
}

export interface RegionCountResponse {
  new_count: {
    by_region: Array<ByRegionCount>;
    total: TotalCount;
  };
  archive_count: {
    by_region: Array<ByRegionCount>;
    total: TotalCount;
  };
}
