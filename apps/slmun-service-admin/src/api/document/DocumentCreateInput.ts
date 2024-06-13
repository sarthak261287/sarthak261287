import { InputJsonValue } from "../../types";

export type DocumentCreateInput = {
  file?: InputJsonValue;
  name?: string | null;
  typeField?: "Option1" | null;
};
