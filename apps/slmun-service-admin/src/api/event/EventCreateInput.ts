import { RegistrationCreateNestedManyWithoutEventsInput } from "./RegistrationCreateNestedManyWithoutEventsInput";

export type EventCreateInput = {
  date?: Date | null;
  description?: string | null;
  location?: string | null;
  registrations?: RegistrationCreateNestedManyWithoutEventsInput;
  title?: string | null;
};
