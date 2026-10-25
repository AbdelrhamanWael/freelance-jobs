'use server'

import prisma from '@/lib/prisma'
import { revalidatePath } from 'next/cache'

export async function getClasses() {
  return await prisma.class.findMany({
    include: {
      _count: {
        select: { students: true }
      }
    },
    orderBy: { createdAt: 'desc' }
  })
}

export async function addClass(formData: FormData): Promise<void> {
  const name = formData.get('name') as string
  if (!name) return

  await prisma.class.create({
    data: { name }
  })

  revalidatePath('/dashboard/classes')
}

export async function deleteClass(id: string): Promise<void> {
  await prisma.class.delete({
    where: { id }
  })
  
  revalidatePath('/dashboard/classes')
}
