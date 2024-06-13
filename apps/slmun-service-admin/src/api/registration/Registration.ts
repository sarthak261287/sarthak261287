import { Event } from "../event/Event";
import { User } from "../user/User";

export type Registration = {
  createdAt: Date;
  event?: Event | null;
  id: string;
  registrationDate: Date | null;
  updatedAt: Date;
  user?: User | null;
};
