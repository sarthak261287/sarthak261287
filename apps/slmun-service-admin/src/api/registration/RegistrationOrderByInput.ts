import { SortOrder } from "../../util/SortOrder";

export type RegistrationOrderByInput = {
  createdAt?: SortOrder;
  eventId?: SortOrder;
  id?: SortOrder;
  registrationDate?: SortOrder;
  updatedAt?: SortOrder;
  userId?: SortOrder;
};
