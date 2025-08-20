class Cube:
    def __init__(self):
        # Define the vertices of the cube
        # Assuming a unit cube centered at the origin for simplicity
        self.vertices = [
            [-0.5, -0.5, -0.5],  # 0
            [ 0.5, -0.5, -0.5],  # 1
            [ 0.5,  0.5, -0.5],  # 2
            [-0.5,  0.5, -0.5],  # 3
            [-0.5, -0.5,  0.5],  # 4
            [ 0.5, -0.5,  0.5],  # 5
            [ 0.5,  0.5,  0.5],  # 6
            [-0.5,  0.5,  0.5]   # 7
        ]

        # Define the faces of the cube using indices into the vertices list
        # Each face is a list of vertex indices in a specific order
        # Front face:
        # 0 --- 1
        # |     |
        # 3 --- 2
        self.faces = [
            [0, 1, 2, 3],  # Front face
            [4, 5, 6, 7],  # Back face
            [0, 4, 7, 3],  # Left face
            [1, 5, 6, 2],  # Right face
            [0, 1, 5, 4],  # Bottom face
            [2, 3, 7, 6]   # Top face
        ]

    def get_vertices(self):
        return self.vertices

    def get_faces(self):
        return self.faces

if __name__ == '__main__':
    # Example usage:
    my_cube = Cube()
    print("Vertices:")
    for i, vertex in enumerate(my_cube.get_vertices()):
        print(f"Vertex {i}: {vertex}")

    print("\nFaces:")
    for i, face in enumerate(my_cube.get_faces()):
        print(f"Face {i}: {face}")