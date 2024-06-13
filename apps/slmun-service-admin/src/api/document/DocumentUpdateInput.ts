import { InputJsonValue } from "../../types";

export type DocumentUpdateInput = {
  file?: InputJsonValue;
  name?: string | null;
  typeField?: "Option1" | null;
};
