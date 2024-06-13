import { Registration as TRegistration } from "../api/registration/Registration";

export const REGISTRATION_TITLE_FIELD = "id";

export const RegistrationTitle = (record: TRegistration): string => {
  return record.id?.toString() || String(record.id);
};
