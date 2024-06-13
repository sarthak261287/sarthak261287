import { JsonValue } from "type-fest";

export type Document = {
  createdAt: Date;
  file: JsonValue;
  id: string;
  name: string | null;
  typeField?: "Option1" | null;
  updatedAt: Date;
};
