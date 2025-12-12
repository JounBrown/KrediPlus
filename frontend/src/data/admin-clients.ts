export type ClientRecord = {
  id: number
  createdAt: string
  nombreCompleto: string
  cedula: string
  email: string
  telefono: string
  fechaNacimiento: string
  direccion: string
  infoAdicional: string
}

export const initialClients: ClientRecord[] = [
  {
    id: 1,
    createdAt: '2024-10-12T10:00:00.000Z',
    nombreCompleto: 'Andrea Ríos',
    cedula: '1034567890',
    email: 'andrea.rios@email.com',
    telefono: '3125556677',
    fechaNacimiento: '1989-05-14',
    direccion: 'Cra 15 #120-45, Bogotá',
    infoAdicional: 'Cliente con buen historial, interesada en ampliación de cupo.',
  },
  {
    id: 2,
    createdAt: '2024-09-30T08:30:00.000Z',
    nombreCompleto: 'Luis Peña',
    cedula: '987654321',
    email: 'luis.pena@email.com',
    telefono: '3001112233',
    fechaNacimiento: '1978-11-02',
    direccion: 'Cll 45 #12-80, Medellín',
    infoAdicional: 'Solicita crédito para remodelación. Esperando documentos.',
  },
  {
    id: 3,
    createdAt: '2024-11-05T14:20:00.000Z',
    nombreCompleto: 'María Gómez',
    cedula: '456789123',
    email: 'maria.gomez@email.com',
    telefono: '3169874560',
    fechaNacimiento: '1965-03-28',
    direccion: 'Av. Boyacá #85-12, Bogotá',
    infoAdicional: 'Reportada en centrales, requiere seguimiento cercano.',
  },
]
