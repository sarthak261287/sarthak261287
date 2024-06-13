import { RegistrationUpdateManyWithoutEventsInput } from "./RegistrationUpdateManyWithoutEventsInput";

export type EventUpdateInput = {
  date?: Date | null;
  description?: string | null;
  location?: string | null;
  registrations?: RegistrationUpdateManyWithoutEventsInput;
  title?: string | null;
};
