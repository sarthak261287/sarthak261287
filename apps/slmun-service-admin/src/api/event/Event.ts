import { Registration } from "../registration/Registration";

export type Event = {
  createdAt: Date;
  date: Date | null;
  description: string | null;
  id: string;
  location: string | null;
  registrations?: Array<Registration>;
  title: string | null;
  updatedAt: Date;
};
