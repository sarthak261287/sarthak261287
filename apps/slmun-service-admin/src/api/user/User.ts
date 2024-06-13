import { Registration } from "../registration/Registration";
import { JsonValue } from "type-fest";

export type User = {
  createdAt: Date;
  email: string | null;
  firstName: string | null;
  id: string;
  lastName: string | null;
  registrations?: Array<Registration>;
  roles: JsonValue;
  updatedAt: Date;
  username: string;
};
