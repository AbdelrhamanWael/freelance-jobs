'use server'

import prisma from '@/lib/prisma'
import { revalidatePath } from 'next/cache'

export async function getStudents() {
  return await prisma.student.findMany({
    include: {
      class: true
    },
    orderBy: { createdAt: 'desc' }
  })
}

export async function addStudent(formData: FormData): Promise<void> {
  const name = formData.get('name') as string
  const classId = formData.get('classId') as string
  
  if (!name || !classId) return

  await prisma.student.create({
    data: { name, classId }
  })

  revalidatePath('/dashboard/students')
}

export async function deleteStudent(id: string): Promise<void> {
  await prisma.student.delete({
    where: { id }
  })
  
  revalidatePath('/dashboard/students')
}
